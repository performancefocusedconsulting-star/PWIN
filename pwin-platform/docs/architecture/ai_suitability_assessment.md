# AI Suitability Assessment — All L3 Tasks

**Version:** 1.0 | April 2026
**Purpose:** Assess every L3 task across all 84 activities for AI suitability, value proposition, and impact on roles, decision velocity, time, and cost.
**Scope:** 295 L3 tasks across 10 workstreams, 3 archetypes.

---

## Rating Framework

### AI Suitability
- **High** — AI can execute autonomously or near-autonomously. Human reviews output.
- **Medium** — AI accelerates significantly but human judgement required for key decisions.
- **Low** — Fundamentally human activity. AI provides minimal support at best.

### Value Dimensions
- **Decision Velocity** — Does AI speed up decision-making? (e.g., faster go/no-go with better data)
- **Time Reduction** — How much elapsed time does AI save? (expressed as % reduction)
- **Cost Reduction** — Does it reduce bid cost (person-days) or delivery cost?
- **Quality Uplift** — Does AI improve the quality of the output beyond what humans typically achieve?

### Impact Notation
- **Role** — Who benefits most from AI on this task
- **Blocker** — What prevents AI from doing more (data access, judgement, client interaction)

---

## Executive Summary

| Suitability | Task Count | % of Total | Key Value |
|---|---|---|---|
| **High** | ~85 | 29% | Automate document analysis, extraction, mapping, consolidation, reporting. Saves 40-60% time on these tasks. |
| **Medium** | ~130 | 44% | AI drafts, human refines. Strategy, modelling, assessment tasks where AI provides first-pass analysis. Saves 30-50% time. |
| **Low** | ~80 | 27% | Human relationships, governance, negotiation, presentation. AI provides preparation support only. Saves 10-20% time. |

**Headline impact:** AI could reduce overall bid elapsed time by **30-40%** and bid cost (person-days) by **25-35%** across a typical services bid. The biggest gains are in SAL (intelligence gathering), SOL (requirements analysis, risk consolidation), COM (financial modelling), and PRD (drafting, compliance, evidence).

---

## SAL — Sales & Capture

### SAL-01: Customer Engagement & Intelligence Gathering

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SAL-01.1.1 Gather procurement documentation | **High** | Scrape Contracts Finder/FTS, extract key data from OJEU notices, compile procurement context automatically | Contracts Finder API, FTS data, OJEU notice | **Decision velocity:** Capture Lead has procurement context in hours not days | Capture Lead | 60% |
| SAL-01.1.2 Review client strategic plans | **High** | Analyse published strategies, spending reviews, annual reports. Extract priorities, budget pressures, policy drivers | Client published documents (PDFs, web pages) | **Quality uplift:** AI reads more documents more thoroughly than a human under time pressure | Capture Lead | 50% |
| SAL-01.1.3 Compile market/sector intelligence | **High** | Scan trade press, analyst reports, sector publications. Synthesise relevant trends | Web search, trade press archives, sector reports | **Time reduction:** Hours of manual research compressed to minutes | Capture Lead | 70% |
| SAL-01.1.4 Map client's strategic suppliers | **High** | Analyse Contracts Finder award history, cross-reference with Companies House, identify supplier relationships | Contracts Finder API, Companies House API | **Decision velocity:** Supplier landscape available immediately, not after days of manual research | Capture Lead | 70% |
| SAL-01.2.1 Identify buyer values and hot buttons | **Medium** | AI drafts buyer values from document analysis. Human validates against relationship intelligence | SAL-01.1 outputs + CRM data | **Quality uplift:** AI surfaces values human might miss from document volume | Capture Lead | 40% |
| SAL-01.2.2 Analyse client problem statement | **Medium** | AI synthesises the "why" from strategic context. Human validates interpretation | SAL-01.1 + SAL-01.2.1 outputs | **Decision velocity:** Problem statement drafted faster, refined by human | Capture Lead | 40% |
| SAL-01.2.3 Synthesise customer intelligence briefing | **Medium** | AI consolidates all upstream outputs into structured briefing. Human reviews and adds relationship intelligence | All SAL-01 outputs | **Time reduction:** Consolidation automated, human focuses on insight | Capture Lead | 50% |

**SAL-01 summary:** 4 High, 3 Medium. AI transforms intelligence gathering from weeks of manual research into hours of AI-assisted analysis with human validation. **Biggest blocker:** Access to client-specific CRM data and relationship intelligence that isn't in public documents.

---

### SAL-02: Incumbent Performance Review

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SAL-02.1.1 Review incumbent SLA performance | **High** | Analyse published performance data, FOI responses, audit reports. Extract KPI performance | Published performance reports, FOI data | **Quality uplift:** Systematic analysis across all available data, not selective reading | Capture Lead | 60% |
| SAL-02.1.2 Assess incumbent culture/partnership | **Medium** | Analyse public sentiment (press, Glassdoor, client publications). Human adds relationship intelligence | Public domain sources + CRM | **Blocker:** Real sentiment comes from relationships, not documents | Capture Lead | 30% |
| SAL-02.1.3 Assess incumbent innovation | **High** | Scan for published innovation evidence — awards, case studies, press releases, patent filings | Public domain sources | **Time reduction:** Comprehensive scan vs selective manual search | Capture Lead | 60% |
| SAL-02.2.1 Assess incumbent price competitiveness | **Medium** | Analyse contract values from Contracts Finder, model price trajectory, benchmark against market | Contracts Finder data, benchmarks | **Decision velocity:** Price position analysis available faster | Commercial Lead | 50% |
| SAL-02.2.2 Assess transition stickiness | **Medium** | Analyse published TUPE/workforce data, contract complexity indicators | Public data, ITT documentation | **Blocker:** Much stickiness data is not publicly available | Capture Lead | 30% |
| SAL-02.3.1 Identify transformational opportunities | **Medium** | Scan technology landscape, map AI/automation capabilities to incumbent operating model gaps | Technology landscape data, SAL-02.1 outputs | **Quality uplift:** AI identifies more technology opportunities than manual brainstorming | Solution Architect | 40% |
| SAL-02.3.2 Assess evaluation alignment | **Medium** | Cross-reference transformation opportunities against ITT evaluation criteria | SAL-02.3.1 + SAL-05 outputs | **Decision velocity:** Alignment assessment automated | Capture Lead | 40% |
| SAL-02.3.3 Assess capability to deliver disruption | **Low** | AI can check credentials library. But capability assessment requires organisational self-knowledge | Internal capability data | **Blocker:** Honest self-assessment is human judgement | Capture Lead | 20% |
| SAL-02.3.4 Model commercial impact of disruption | **Medium** | AI can run financial models on cost base changes | Financial model, SAL-02.3.1 outputs | **Time reduction:** Modelling automated, assumptions human | Commercial Lead | 50% |
| SAL-02.3.5 Synthesise incumbent assessment | **Medium** | AI consolidates all 9 upstream outputs. Human validates | All SAL-02 outputs | **Time reduction:** Consolidation automated | Capture Lead | 50% |

**SAL-02 summary:** 2 High, 7 Medium, 1 Low. AI is strongest on public-domain research and financial modelling. Weakest on relationship intelligence and honest self-assessment.

---

### SAL-03: Competitor Analysis & Positioning (Gold Standard Reference)

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SAL-03.1.1 Identify credible competitors | **High** | Analyse Contracts Finder history, framework incumbents, market intelligence to build competitor long-list | Contracts Finder API, framework data | **Time reduction:** Competitor identification automated | Capture Lead | 70% |
| SAL-03.1.2 Categorise competitors | **Medium** | AI proposes categorisation based on data. Human validates with market knowledge | SAL-03.1.1 + market intelligence | **Decision velocity:** Draft categorisation available immediately | Capture Lead | 40% |
| SAL-03.1.3 Profile each competitor | **High** | Build competitor profiles from public data — annual reports, award history, press, LinkedIn, financial filings | Public domain + Companies House | **Quality uplift:** More comprehensive profiles than manual research typically produces | Capture Lead | 60% |
| SAL-03.2.1 Develop counter-strategies | **Medium** | AI proposes counter-strategies based on profiles. Human applies competitive judgement | SAL-03.1 outputs | **Blocker:** Counter-strategy requires human competitive instinct | Capture Lead | 30% |
| SAL-03.2.2 Validate competitive positioning | **Low** | AI prepares the briefing pack. Human team debates and validates | All SAL-03 outputs | **Blocker:** Team validation is a human workshop | Bid Team | 10% |

**SAL-03 summary:** 2 High, 2 Medium, 1 Low.

---

### SAL-04: Win Theme Development & Refinement

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SAL-04.1.1 Import/develop win themes | **Medium** | AI proposes themes from buyer values + competitive positioning. Human refines | SAL-01, SAL-02, SAL-03 outputs | **Decision velocity:** Draft themes available instantly for human refinement | Capture Lead | 40% |
| SAL-04.1.2 Test themes against buyer values | **High** | AI maps themes to buyer values systematically — coverage matrix | SAL-04.1.1 + SAL-01.2.1 | **Quality uplift:** Systematic mapping catches gaps human might miss | Capture Lead | 60% |
| SAL-04.1.3 Test themes against competitive positioning | **Medium** | AI assesses whether competitors can claim the same thing. Human applies judgement | SAL-04.1.1 + SAL-03 outputs | **Decision velocity:** Competitive differentiation assessment automated | Capture Lead | 40% |
| SAL-04.1.4 Ensure themes are evidence-backed | **High** | AI searches evidence library for substantiation per theme | Evidence library, credentials database | **Time reduction:** Library search automated | Bid Manager | 70% |
| SAL-04.2.1 Refine themes against ITT | **Medium** | AI aligns language to ITT terminology. Human validates nuance | SAL-04.1 outputs + ITT docs | **Quality uplift:** AI ensures consistent ITT language alignment | Capture Lead | 40% |
| SAL-04.2.2 Develop messaging per theme | **Medium** | AI drafts messaging. Human refines for strategic impact | SAL-04.2.1 outputs | **Time reduction:** First draft automated | Capture Lead | 40% |
| SAL-04.2.3 Validate with bid team | **Low** | AI prepares validation pack. Human team debates | All SAL-04 outputs | **Blocker:** Team validation is human | Bid Team | 10% |

**SAL-04 summary:** 2 High, 4 Medium, 1 Low.

---

### SAL-05: Evaluation Criteria Mapping & Scoring Strategy

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SAL-05.1.1 Deconstruct evaluation methodology | **High** | AI extracts criteria, weightings, thresholds from ITT documentation | ITT evaluation documents | **Time reduction:** Extraction that takes hours done in minutes | Bid Manager | 70% |
| SAL-05.1.2 Map criteria to response sections | **High** | AI maps criteria to sections, calculates marks-per-page ratio | SAL-05.1.1 + ITT response structure | **Quality uplift:** Systematic mapping, no sections missed | Bid Manager | 60% |
| SAL-05.1.3 Analyse scoring guidance | **High** | AI extracts grade descriptors, identifies differentiating phrases per band | Client marking scheme | **Decision velocity:** Scoring guidance analysis instant if document available | Bid Manager | 70% |
| SAL-05.2.1 Analyse marks concentration | **High** | AI ranks sections by marks value, categorises strategic importance | SAL-05.1.2 output | **Decision velocity:** Effort prioritisation available immediately | Bid Manager | 80% |
| SAL-05.2.2 Score gap analysis | **Medium** | AI identifies gaps by cross-referencing scoring requirements with capability/evidence data. Human validates | SAL-05.1.3 + evidence library + capability data | **Quality uplift:** Systematic gap identification across all sections | Bid Manager | 50% |
| SAL-05.2.3 Per-section scoring strategy | **Medium** | AI drafts strategy per section based on scoring guidance. Human refines | SAL-05.2.1 + SAL-05.2.2 | **Time reduction:** Draft strategies automated | Bid Manager | 40% |
| SAL-05.2.4 Align win themes to sections | **High** | AI maps themes to sections — produces integration matrix | SAL-04 + SAL-05.2.3 | **Quality uplift:** Ensures no theme orphaned from high-value sections | Bid Manager | 70% |
| SAL-05.2.5 Confirm with bid team | **Low** | AI prepares briefing pack. Human team confirms | All SAL-05 outputs | **Blocker:** Team confirmation is human | Bid Team | 10% |

**SAL-05 summary:** 5 High, 2 Medium, 1 Low. **This is one of the highest-value AI workstreams.** Evaluation analysis is document-heavy, systematic, and pattern-based — perfect for AI.

---

### SAL-06: Capture Plan Finalisation & Win Strategy Lock

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SAL-06.1.1 Assess capture effectiveness | **Medium** | AI compares capture plan assumptions against ITT documentation | SAL-06 inputs + ITT docs | **Decision velocity:** Alignment gaps identified automatically | Capture Lead | 40% |
| SAL-06.1.2 Rapid ITT documentation analysis | **High** | AI analyses requirements, contract, payment mechanism, SLAs in the ITT pack | Full ITT documentation pack | **Time reduction:** Days of manual ITT analysis compressed to hours. **This is a killer AI use case.** | Bid Manager | 70% |
| SAL-06.2.1 Complete DQC | **Medium** | AI pre-populates DQC from upstream outputs. Human validates and scores | All SAL outputs | **Decision velocity:** DQC largely pre-filled, human focuses on judgement calls | Bid Director | 40% |
| SAL-06.2.2 Assess strategic fit | **Low** | Requires organisational strategic knowledge | Strategic plan, pipeline data | **Blocker:** Internal strategic judgement | Bid Director | 20% |
| SAL-06.2.3 Score PWIN | **Medium** | AI calculates PWIN from structured inputs across all dimensions | All dimension inputs | **Decision velocity:** Quantified PWIN with evidence basis, not gut feel | Bid Director | 50% |
| SAL-06.2.4 Synthesise win strategy | **Medium** | AI drafts the narrative from upstream outputs. Human refines | All SAL outputs | **Time reduction:** First draft automated | Bid Director | 40% |
| SAL-06.3.1 Define consortium strategy | **Low** | Strategic partnership decisions require human judgement | Market knowledge, relationships | **Blocker:** Consortium design is a strategic human decision | Bid Director | 10% |
| SAL-06.3.2 Identify partner capabilities | **Medium** | AI maps gaps to potential partner types from market data | SAL-05.2.2 + SAL-02.3.3 + market data | **Time reduction:** Gap-to-partner mapping automated | Capture Lead | 40% |
| SAL-06.3.3 Define work breakdown | **Low** | Requires strategic design judgement | Consortium strategy | **Blocker:** Work breakdown is a design decision | Bid Director | 10% |
| SAL-06.4.1 Assemble capture plan | **High** | AI consolidates all upstream outputs into structured document | All SAL-06 upstream outputs | **Time reduction:** Document assembly automated | Bid Manager | 60% |
| SAL-06.4.2 Prepare bid mandate | **Medium** | AI drafts mandate from capture plan. Human positions for governance | SAL-06.4.1 output | **Time reduction:** Draft automated | Bid Director | 40% |
| SAL-06.4.3 Confirm lock | **Low** | Formal sign-off is a human governance act | SAL-06.4.1 + SAL-06.4.2 | **Blocker:** Governance is human | Bid Director | 0% |

**SAL-06 summary:** 2 High, 5 Medium, 4 Low (1 at 0%). The rapid ITT analysis (SAL-06.1.2) is one of the highest-value AI applications in the entire methodology.

---

### SAL-07: Pre-submission Clarification Strategy & Drafting

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SAL-07.1.1 Harvest clarification needs from ITT | **High** | AI identifies ambiguities, contradictions, and gaps in ITT documentation automatically | ITT documentation, SAL-06.1.2 | **Quality uplift:** AI catches ambiguities human might miss across large document sets | Bid Manager | 60% |
| SAL-07.1.2 Harvest from workstreams | **Medium** | AI consolidates clarification needs raised by each workstream. Human prioritises | SOL-01, SAL-05.2.2 outputs | **Time reduction:** Consolidation automated | Bid Manager | 40% |
| SAL-07.1.3 Develop competitive clarification strategy | **Low** | Competitive gaming requires human strategic thinking | Win strategy, competitive intelligence | **Blocker:** Gaming strategy is fundamentally human — incumbent vs challenger playbooks | Capture Lead | 10% |
| SAL-07.2.1 Categorise and prioritise | **High** | AI categorises by type and proposes priority ranking based on scoring impact | SAL-07.1 outputs | **Decision velocity:** Priority ranking available immediately | Bid Manager | 60% |
| SAL-07.2.2 Draft questions with strategic intent | **Medium** | AI drafts neutral question language. Human adds strategic framing | SAL-07.2.1 + competitive strategy | **Blocker:** Strategic framing requires human judgement on what to reveal | Capture Lead | 30% |
| SAL-07.2.3 Vet and approve | **Low** | Approval is a human governance act | Drafted questions | **Blocker:** Approval is human | Bid Director | 0% |

**SAL-07 summary:** 2 High, 2 Medium, 2 Low.

---

### SAL-10: Stakeholder Relationship Mapping & Engagement

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SAL-10.1.1 Identify DMU | **High** | AI scrapes org charts, LinkedIn, published structures to build initial DMU map | Client org data, LinkedIn, published structures | **Time reduction:** Initial map built automatically, human validates and adds intel | Capture Lead | 50% |
| SAL-10.1.2 Assess influence and disposition | **Low** | Requires relationship intelligence that isn't in documents | CRM, human knowledge | **Blocker:** Disposition assessment is relationship-based human judgement | Capture Lead | 10% |
| SAL-10.1.3 Map relationship strength | **Low** | Requires internal relationship knowledge | CRM, human knowledge | **Blocker:** "Who knows whom" is human knowledge | Account Manager | 10% |
| SAL-10.2.1 Develop engagement plan | **Medium** | AI proposes engagement approach per stakeholder type. Human refines | SAL-10.1 outputs | **Decision velocity:** Draft plan available immediately | Capture Lead | 30% |
| SAL-10.2.2 Execute engagements and log | **Low** | AI can't attend meetings. Can structure the log template | N/A | **Blocker:** Engagement is fundamentally face-to-face human activity | Account Manager | 5% |
| SAL-10.2.3 Update stakeholder map | **Medium** | AI updates the map from logged engagement data. Human validates shifts | Engagement log data | **Time reduction:** Map update automated from structured log entries | Capture Lead | 40% |

**SAL-10 summary:** 1 High, 2 Medium, 3 Low. Stakeholder management is heavily relationship-dependent — AI helps with research but not with relationships.

---

## SOL — Solution Design

### SOL-01: Requirements Analysis & Interpretation

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SOL-01.1.1 Decompose ITT into requirements | **High** | AI extracts every requirement from spec, schedules, annexes, contract — structured and cross-referenced | Full ITT document pack | **This is a top-5 AI use case.** Days of manual extraction done in hours. Cross-referencing across documents catches hidden requirements. | Solution Architect | 70% |
| SOL-01.1.2 Categorise requirements | **High** | AI categorises each requirement by type, priority, scoring linkage | SOL-01.1.1 output + SAL-05 | **Quality uplift:** Systematic categorisation, no requirements missed | Solution Architect | 60% |
| SOL-01.1.3 Identify ambiguities and gaps | **High** | AI identifies contradictions between documents, missing requirements, unstated assumptions | SOL-01.1.2 + industry standards | **Quality uplift:** AI cross-references at scale — catches contradictions humans miss | Solution Architect | 60% |
| SOL-01.2.1 Interpret against buyer values | **Medium** | AI maps requirements to buyer values, proposes interpretation. Human validates | SOL-01.1.2 + SAL-01.2.1 | **Blocker:** Interpretation requires domain judgement | Solution Architect | 30% |
| SOL-01.2.2 Assess solution alignment | **Medium** | AI assesses alignment if capability data is structured. Human validates gaps | SOL-01.2.1 + capability data | **Blocker:** Requires structured internal capability data | Solution Architect | 40% |
| SOL-01.2.3 Synthesise interpretation document | **High** | AI consolidates all upstream outputs into structured document | All SOL-01 outputs | **Time reduction:** Assembly automated | Solution Architect | 60% |

**SOL-01 summary:** 4 High, 2 Medium. **Requirements analysis is the single highest-value AI workstream.** Document decomposition and cross-referencing is what AI does better than humans at scale.

---

### SOL-02: Current Operating Model Assessment

| Task | AI Rating | What AI Does | Inputs Needed | Value Proposition | Role Impact | Time Reduction |
|---|---|---|---|---|---|---|
| SOL-02.1.1 Map organisational structure | **Medium** | AI extracts structure from published documents. Human fills gaps | Published data, ITT docs | **Blocker:** Often limited published data about current operating model | Solution Architect | 30% |
| SOL-02.1.2 Assess current workforce | **Medium** | AI analyses disclosed TUPE data. Human interprets gaps | TUPE data (if disclosed) | **Blocker:** TUPE data often incomplete or not yet disclosed | HR Lead | 30% |
| SOL-02.1.3 Review technology landscape | **Medium** | AI analyses published technology references in ITT/contract docs | ITT documentation | **Blocker:** Current technology landscape rarely documented in detail | Technical Lead | 30% |
| SOL-02.2.1 Assess current performance | **High** | AI analyses published KPI/performance data, audit reports, FOI responses | Published performance data | **Quality uplift:** Comprehensive data analysis across all available sources | Solution Architect | 50% |
| SOL-02.2.2 Document operating model | **Medium** | AI synthesises the integrated operating model from upstream outputs | SOL-02.1 outputs | **Time reduction:** Synthesis automated | Solution Architect | 40% |
| SOL-02.2.3 Identify day-one inheritance | **Medium** | AI identifies transfer implications from document analysis. Human validates | SOL-02.2.2 output | **Decision velocity:** Transition implications surfaced faster | Solution Architect | 30% |

**SOL-02 summary:** 1 High, 5 Medium. Limited by data availability — much as-is operating model information isn't publicly available.

---

### SOL-03 through SOL-12 (Summary Table)

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **SOL-03** TOM design | 0 | 5 | 4 | AI drafts design options against requirements. Human designs. | Design is creative human work |
| **SOL-04** Service delivery | 0 | 4 | 2 | AI maps processes to requirements. Human designs processes. | Process design is human expertise |
| **SOL-05** Technology | 1 | 4 | 1 | AI assesses technology options, maps security requirements | Build/buy decisions need organisational context |
| **SOL-06** Staffing/TUPE | 1 | 3 | 1 | AI models workforce costs, maps TUPE terms | TUPE data often incomplete |
| **SOL-07** Transition | 0 | 4 | 2 | AI drafts phase plans from SOL outputs. Human validates | Transition planning requires delivery experience |
| **SOL-08** Innovation | 1 | 5 | 2 | AI scans technology landscape, models productivity curve | Innovation strategy is human creative work |
| **SOL-09** Social value | 1 | 3 | 1 | AI analyses local area data, maps commitments to SV model | Local knowledge and commitment design is human |
| **SOL-10** Evidence | 3 | 2 | 1 | **AI searches evidence library, identifies gaps, matches evidence to sections** | Evidence library must be structured and accessible |
| **SOL-11** Solution lock | 1 | 2 | 1 | AI runs coherence checks across solution components | Design validation requires human judgement |
| **SOL-12** Solution risk | 2 | 2 | 1 | AI consolidates risks from all activities automatically | Risk assessment requires domain expertise |

**SOL summary:** 10 High, 34 Medium, 16 Low. SOL-01 and SOL-10 are the highest-value AI targets.

---

## COM — Commercial & Pricing

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **COM-01** Should-cost model | 2 | 4 | 1 | **AI builds cost model from structured staffing/technology data.** Automates year-on-year trajectory. | Assumptions require commercial judgement |
| **COM-02** Price-to-win | 2 | 3 | 1 | AI analyses Contracts Finder data, benchmarks, models price envelope | Competitor price intelligence is limited |
| **COM-03** Partner pricing | 1 | 3 | 2 | AI validates partner submissions against our model. Human negotiates | Negotiation is human |
| **COM-04** Commercial model | 0 | 4 | 2 | AI maps ITT payment provisions. Human designs commercial approach | Commercial design is strategic judgement |
| **COM-05** Margin/sensitivity | 3 | 1 | 1 | **AI runs all sensitivity analysis and stress tests automatically.** Tornado charts, scenarios, break-even. | Assumptions and risk appetite are human |
| **COM-06** Pricing lock | 1 | 2 | 1 | AI reconciles cost model to pricing schedules, checks arithmetic | Pricing decisions are human/governance |
| **COM-07** Commercial risk | 2 | 2 | 1 | AI consolidates risks, cross-references sensitivities | Risk acceptance is human governance |

**COM summary:** 11 High, 19 Medium, 9 Low. **COM-05 (sensitivity analysis) is almost entirely automatable** — financial modelling and scenario testing is what AI excels at. COM-01 (cost modelling) is highly automatable once inputs are structured.

---

## LEG — Legal & Contractual

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **LEG-01** Contract review | 2 | 1 | 1 | **AI analyses contract clauses, identifies non-standard terms, compares to corporate playbook.** | Legal judgement on acceptability is human |
| **LEG-02** Risk allocation | 1 | 2 | 0 | AI maps risk allocation across contract categories | Risk appetite decisions are human |
| **LEG-03** Insurance | 1 | 1 | 1 | AI extracts insurance requirements, compares to current coverage | Procurement of new coverage is operational |
| **LEG-04** TUPE legal | 0 | 2 | 1 | AI analyses TUPE regulations against staffing plan | Legal judgement on compliance is human |
| **LEG-05** Data protection | 1 | 1 | 1 | AI drafts DPIA from technology design, identifies data processing | DPIA validation requires legal sign-off |
| **LEG-06** Subcontractor terms | 1 | 1 | 1 | AI compares partner terms to prime contract for flow-down gaps | Negotiation strategy is human |

**LEG summary:** 6 High, 8 Medium, 5 Low. **Contract analysis (LEG-01) is high-value AI** — AI can read and flag non-standard clauses faster than lawyers.

---

## DEL — Programme & Delivery

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **DEL-01** Risk register | 1 | 2 | 1 | AI consolidates risks from all sources | Risk judgement is human |
| **DEL-02** Mobilisation | 0 | 3 | 1 | AI drafts programme from SOL-07 transition plan | Programme design requires delivery experience |
| **DEL-03** Performance framework | 1 | 1 | 1 | AI maps ITT KPIs to delivery components, designs monitoring | Confidence assessment is human |
| **DEL-04** Resource plan | 0 | 2 | 1 | AI maps resource needs from staffing model to timeline | Resource judgement is human |
| **DEL-05** BC/exit | 1 | 1 | 0 | AI drafts BC/DR and exit plan from solution design | Planning is straightforward once design exists |
| **DEL-06** Risk mitigation | 1 | 1 | 1 | AI consolidates all risk registers for governance | Risk acceptance is human governance |

**DEL summary:** 4 High, 10 Medium, 5 Low.

---

## SUP — Supply Chain & Partners

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **SUP-01** Partner selection | 1 | 1 | 1 | AI searches market databases for matching partners | Due diligence requires human assessment |
| **SUP-02** Partner solution inputs | 0 | 2 | 1 | AI reviews partner submissions for completeness | Integration judgement is human |
| **SUP-03** Teaming agreements | 0 | 1 | 2 | AI reviews standard terms. Negotiation is human | Negotiation is fundamentally human |
| **SUP-04** Partner pricing | 0 | 1 | 1 | AI validates partner pricing against our model | Facilitation/escalation is human |
| **SUP-05** Partner credentials | 1 | 1 | 0 | AI reviews partner evidence for quality/relevance | Collection depends on partner responsiveness |
| **SUP-06** Back-to-back terms | 0 | 1 | 2 | AI compares flow-down alignment. Negotiation is human | Negotiation is human |

**SUP summary:** 2 High, 7 Medium, 7 Low. Supply chain is relationship-heavy — AI helps with analysis but not with negotiation.

---

## BM — Bid Management

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **BM-01** Kickoff | 0 | 1 | 1 | AI drafts programme from template. Human confirms | Kickoff is a human leadership event |
| **BM-02** BMP | 1 | 0 | 0 | AI drafts BMP from template + capture plan | Standard document assembly |
| **BM-03** Doc management | 1 | 0 | 0 | AI configures repository from template. Human confirms | Straightforward automation |
| **BM-04** Resource tracking | 0 | 1 | 1 | AI tracks from team roster data. Human manages changes | Change management is human |
| **BM-05** Cost tracking | 1 | 0 | 0 | AI automates budget vs actual tracking | Standard financial tracking |
| **BM-06** Progress reporting | 1 | 1 | 0 | **AI generates progress reports from activity status data automatically** | Report generation, not insight |
| **BM-07** Quality plan | 1 | 1 | 0 | AI generates page budgets from marks analysis (SAL-05) | Quality standards need human calibration |
| **BM-08** Stakeholder comms | 0 | 1 | 0 | AI drafts comms plan. Human manages relationships | Stakeholder management is human |
| **BM-09** Competitive dialogue | 0 | 1 | 1 | AI prepares briefing packs. Sessions are human | Dialogue is fundamentally human interaction |
| **BM-10** Storyboard | 1 | 1 | 1 | **AI drafts storyboard structure from win themes + scoring strategy + solution design.** Human refines | Storyboard design requires creative judgement |
| **BM-11** Hot debrief | 0 | 0 | 1 | AI structures the debrief template | Debrief is a human conversation |
| **BM-12** Lessons learned | 1 | 1 | 1 | AI analyses review scores, identifies patterns. Human draws lessons | Pattern analysis is AI-suitable |
| **BM-13** Bid risk register | 1 | 1 | 0 | **AI consolidates all workstream risks automatically, identifies duplicates, flags gaps** | Risk judgement is human |
| **BM-14** Clarification ops | 1 | 1 | 0 | AI tracks submissions, logs responses, distributes to workstreams | Operational tracking automation |
| **BM-15** Clarification impact | 1 | 1 | 0 | AI triages responses against requirements baseline, flags affected items | Impact identification is systematic |
| **BM-16** Win strategy refresh | 0 | 1 | 1 | AI compares current intelligence to original strategy. Human decides | Strategic reassessment is human |

**BM summary:** 10 High, 12 Medium, 7 Low. BM has many automatable operational tasks — reporting, tracking, consolidation. The management and leadership tasks remain human.

---

## PRD — Proposal Production

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **PRD-01** Compliance matrix | 2 | 0 | 0 | **AI maps requirements to responses automatically, flags compliance gaps.** Top-5 AI use case. | Requires structured requirements data (SOL-01.1) |
| **PRD-02** Section drafting | 1 | 2 | 0 | **AI produces first drafts from storyboard + solution design + win themes.** Human refines. Writers spend time improving, not starting from blank page. | Quality of first draft depends on solution detail |
| **PRD-03** Evidence assembly | 1 | 1 | 0 | AI matches evidence to sections from requirements matrix | Evidence library must be structured |
| **PRD-04** Pricing response | 1 | 1 | 0 | AI populates pricing schedules from COM-06 locked model | Standard data mapping |
| **PRD-05** Pink review | 0 | 1 | 1 | AI can pre-assess storyboard against evaluation criteria. Reviewers still needed | Review judgement is human |
| **PRD-06** Red review | 0 | 1 | 1 | **AI can simulate evaluator scoring against marking scheme.** Reviewers validate | Evaluator simulation requires calibration |
| **PRD-07** Gold review | 0 | 0 | 1 | Executive review is fundamentally human | Governance is human |
| **PRD-08** QA/formatting | 1 | 1 | 0 | AI checks cross-references, word counts, formatting compliance, spelling | Standard QA automation |
| **PRD-09** Submission | 0 | 1 | 1 | AI runs final compliance check against matrix | Portal upload may require human |

**PRD summary:** 6 High, 8 Medium, 4 Low. **PRD-01 (compliance mapping) and PRD-02 (AI-assisted drafting) are transformational.** AI generates first drafts from structured methodology data — writers refine rather than write from scratch.

---

## GOV — Internal Governance

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **GOV-01** Pursuit approval | 1 | 0 | 1 | AI assembles review pack from upstream outputs | Decision is human governance |
| **GOV-02** Solution review | 1 | 0 | 1 | AI assembles review pack | Decision is human governance |
| **GOV-03** Pricing review | 1 | 0 | 1 | AI assembles review pack | Decision is human governance |
| **GOV-04** Executive approval | 1 | 0 | 1 | AI assembles executive summary | Decision is human governance |
| **GOV-05** Submission authority | 0 | 0 | 1 | Formal sign-off is entirely human | Governance is human |
| **GOV-06** Legal review | 1 | 0 | 1 | AI assembles legal review pack | Decision is human governance |

**GOV summary:** 5 High (pack assembly), 0 Medium, 6 Low (decisions). AI assembles every governance pack; humans make every decision. Clean split.

---

## POST — Post-Submission

| Activity | High | Med | Low | Key AI Value | Biggest Blocker |
|---|---|---|---|---|---|
| **POST-01** Presentation design | 0 | 1 | 1 | AI drafts presentation from submitted proposal + win themes | Presentation design is creative |
| **POST-02** Rehearsals | 0 | 0 | 1 | AI can simulate Q&A questions. Rehearsal is human | Human practice |
| **POST-03** Delivery | 0 | 0 | 1 | Cannot be AI'd | Client-facing presentation |
| **POST-04** Post-sub clarifications | 1 | 1 | 0 | AI drafts clarification responses consistent with submitted proposal | Consistency checking is systematic |
| **POST-05** BAFO preparation | 0 | 2 | 0 | AI models price adjustments using sensitivity data from COM-05 | BAFO strategy is human judgement |
| **POST-06** BAFO governance | 0 | 0 | 1 | Governance is human | Human governance |
| **POST-07** Contract negotiation | 0 | 0 | 1 | Cannot be AI'd | Negotiation is human |
| **POST-08** Award/handover | 0 | 1 | 1 | AI assembles handover pack from all bid outputs | Knowledge transfer requires human |

**POST summary:** 1 High, 5 Medium, 6 Low. Post-submission is heavily human — presentations, negotiations, governance.

---

## Top 10 Highest-Value AI Applications

Ranked by combination of time saving, quality uplift, and frequency of use across bids:

| Rank | Task(s) | AI Application | Value | Time Saving | Affected Role |
|---|---|---|---|---|---|
| **1** | SOL-01.1.1-1.1.3 | **ITT requirements extraction and analysis** | Transforms days of manual extraction into hours. Cross-references across documents at scale. Catches hidden requirements. | 60-70% | Solution Architect |
| **2** | PRD-02.1.1 | **AI-assisted response drafting** | AI generates first drafts from storyboard + solution design + win themes. Writers refine, not write from scratch. | 40-50% | Writers |
| **3** | SAL-05.1.1-1.3 | **Evaluation criteria extraction and scoring analysis** | Automatically extracts criteria, weightings, grade descriptors. Produces marks concentration analysis. | 60-80% | Bid Manager |
| **4** | PRD-01.1.1 | **Automated compliance mapping** | Maps every ITT requirement to response sections. Identifies compliance gaps systematically. | 60-70% | Bid Manager |
| **5** | SAL-06.1.2 | **Rapid ITT documentation analysis** | Analyses requirements, contract, payment mechanism, SLAs across the entire ITT pack for go/no-go. | 70% | Bid Manager |
| **6** | COM-05.2.1-2.2 | **Automated sensitivity and stress testing** | Runs all financial scenarios, tornado analysis, break-even modelling from structured cost data. | 70-80% | Commercial Lead |
| **7** | LEG-01.1.1 | **Contract clause analysis** | AI analyses every clause, identifies non-standard terms, compares to corporate playbook, flags risk areas. | 50-60% | Legal Lead |
| **8** | SAL-01.1.1-1.4 | **Customer and market intelligence gathering** | Automated Contracts Finder scraping, client strategy analysis, supplier landscape mapping. | 60-70% | Capture Lead |
| **9** | BM-13.1.1 + SOL-12 + COM-07 | **Automated risk consolidation** | Consolidates all workstream risks, removes duplicates, identifies cross-cutting risks, flags gaps. | 50-60% | Bid Manager |
| **10** | SOL-10.1.1-1.3 | **Evidence gap analysis and library search** | Maps evidence needs to sections, searches library, identifies gaps, prioritises by scoring impact. | 60-70% | Bid Manager |

---

## External Data Sources Required

For AI to deliver on the highest-value applications, these external data connections are needed:

| Data Source | AI Applications It Enables | Priority |
|---|---|---|
| **Contracts Finder / FTS API** | SAL-01 (procurement intel), SAL-02 (incumbent pricing), SAL-03 (competitor identification), COM-02 (price benchmarks) | Critical |
| **Companies House API** | SAL-03 (competitor profiling), SUP-01 (partner due diligence) | High |
| **ITT Document Pack (uploaded)** | SOL-01 (requirements), SAL-05 (evaluation criteria), SAL-06 (ITT analysis), LEG-01 (contract review), PRD-01 (compliance) | Critical |
| **Client Published Documents** | SAL-01 (strategic context), SAL-02 (performance data) | High |
| **Evidence Library (internal)** | SAL-04 (theme substantiation), SOL-10 (evidence strategy), PRD-03 (evidence assembly) | Critical |
| **Corporate Cost Data** | COM-01 (rate cards, overhead rates), COM-02 (benchmarks) | High |
| **Industry Benchmarks (Gartner, ISG)** | COM-02 (market rates), SAL-02 (performance benchmarks) | Medium |
| **CRM / Relationship Data** | SAL-01 (client intel), SAL-10 (stakeholder mapping) | Medium |

---

## Implementation Roadmap — Suggested Skill Build Priority

| Phase | Skills to Build | Tasks Enabled | Business Impact |
|---|---|---|---|
| **Phase 1: Document Intelligence** | ITT extraction, requirements analysis, contract clause analysis, evaluation criteria extraction | SOL-01, SAL-05, SAL-06.1.2, LEG-01, PRD-01 | **Highest impact.** Transforms the first 2 weeks of every bid. Enables faster go/no-go and more informed strategy. |
| **Phase 2: Content Generation** | Response drafting, storyboard generation, governance pack assembly, compliance mapping | PRD-02, BM-10, GOV-01-06, PRD-01 | **Highest visibility.** AI writes first drafts. Bid team sees immediate productivity gain. |
| **Phase 3: Intelligence & Research** | Market scanning, competitor profiling, client intelligence, evidence library search | SAL-01, SAL-02, SAL-03, SOL-10 | **Strategic value.** Better intelligence, faster capture planning. |
| **Phase 4: Financial Modelling** | Cost modelling, sensitivity analysis, price-to-win, margin modelling | COM-01, COM-02, COM-05 | **Commercial value.** Automated financial modelling with scenario testing. |
| **Phase 5: Risk & Consolidation** | Risk register consolidation, assumption tracking, clarification impact analysis | BM-13, SOL-12, COM-07, DEL-06, BM-15 | **Quality uplift.** No risks fall through cracks. |

---

*AI suitability assessment completed — 2026-04-02*
*Based on methodology gold standard: 84 activities, ~295 L3 tasks*
*Aligned with: PWIN Architect Plugin Architecture, Methodology Data Model*
