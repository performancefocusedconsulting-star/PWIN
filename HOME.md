# PWIN - Map of Content

This is the vault home page. Use it to navigate the product family, design documents, agent specs, and project decisions.

---

## Product Family

The PWIN platform is a suite of AI-powered bid management products. Each product sits at a different point in the pursuit lifecycle:

```
Qualify → Strategy → Execution → Verdict
"Should we bid?"   "How do we win?"   "Execute the bid"   "What went wrong?"
```

| Product | Status | Entry point |
|---------|--------|-------------|
| [[CLAUDE|Master reference (CLAUDE.md)]] | Live | Architecture decisions, product state |
| [[pwin-qualify/content/README\|PWIN Qualify]] | Live (two apps) | AI bid qualification & coaching |
| [[pwin-bid-execution/docs/methodology_gold_standard\|PWIN Bid Execution]] | In development | Bid production control & assurance |
| [[pwin-competitive-intel/README\|Competitive Intelligence]] | Built | UK public sector procurement DB |
| [[bidequity-verdict/docs/BidEquity-Verdict-PRD-v2\|BidEquity Verdict]] | Design | Post-loss forensic bid review |
| [[pwin-portfolio/docs/pwin-architect-portfolio-dashboard\|PWIN Portfolio]] | Prototype | Leadership pipeline dashboard |
| PWIN Strategy | Not yet built | Capture-phase strategy development |

---

## Platform & Architecture

- [[pwin-bid-execution/docs/mcp_server_architecture\|MCP Server Architecture]] — the multi-product platform backbone (94 tools, JSON file store)
- [[pwin-bid-execution/docs/pwin_architect_plugin_architecture\|Plugin Architecture]] — agent specs, skill definitions, plugin model
- [[pwin-bid-execution/docs/ai_suitability_assessment\|AI Suitability Assessment]] — which activities benefit from AI
- [[pwin-bid-execution/docs/ai_value_proposition\|AI Value Proposition]] — four-layer value model

---

## AI Agents

Six capability-based agents power the platform. Each has a design spec and (where built) a runtime AGENT.md:

| Agent | Design Spec | Runtime |
|-------|-------------|---------|
| 1. Document Intelligence | [[pwin-bid-execution/docs/agent_1_document_intelligence\|Spec]] | — |
| 2. Market & Competitive Intelligence | [[pwin-bid-execution/docs/agent_2_market_intelligence\|Spec]] | [[pwin-architect-plugin/agents/market-intelligence/AGENT\|AGENT.md]] |
| 3. Strategy & Scoring | [[pwin-bid-execution/docs/agent_3_strategy_scoring\|Spec]] | — |
| 4. Commercial & Financial | [[pwin-bid-execution/docs/agent_4_commercial_financial\|Spec]] | — |
| 5. Content Drafting | [[pwin-bid-execution/docs/agent_5_content_drafting\|Spec]] | — |
| 6. Solution & Delivery | [[pwin-bid-execution/docs/agent_6_solution_delivery\|Spec]] | — |

---

## Bid Execution Methodology

- [[pwin-bid-execution/docs/methodology_gold_standard\|Gold Standard]] — the reference methodology (SAL-03 as template)
- [[pwin-bid-execution/docs/methodology_sol_technology_archetype\|Solution: Technology/Digital]]
- [[pwin-bid-execution/docs/methodology_sol_consulting_archetype\|Solution: Consulting/Advisory]]
- [[pwin-bid-execution/docs/methodology_com_archetype_variants\|Commercial Archetypes]]
- [[pwin-bid-execution/docs/methodology_del_archetype_variants\|Delivery Archetypes]]
- [[pwin-bid-execution/docs/role_based_personas\|Role-Based Personas]]

---

## PWIN Qualify

- [[pwin-qualify/content/README\|Content System]] — how the scoring brain works (JSON content, build script, eval harness)
- [[pwin-qualify/content/qualify-master-spec-v0.1\|Master Spec v0.1]] — content format specification
- [[pwin-qualify/content/rubric-authoring-guide\|Rubric Authoring Guide]] — how to tune rubric bands and inflation signals
- [[pwin-qualify/docs/qualify-execute-alignment-analysis\|Qualify-Execute Alignment]] — mapping between Qualify assessments and Execution activities

---

## Competitive Intelligence

- [[pwin-competitive-intel/README\|Overview & Running]] — architecture, CLI queries, dashboard, FTS/OCP ingest, Companies House enrichment

---

## BidEquity (Brand & Website)

- [[bidequity-co/docs/BidEquity-Website-Implementation-Spec\|Website Implementation Spec]]
- [[bidequity-co/docs/brand-design-system\|Brand Design System]]
- [[bidequity-co/docs/brand-guidelines-v1.2\|Brand Guidelines v1.2]]

---

## Skills & Governance

- [[pwin-platform/skills/agent5-content-drafting/docs/governance-pack-design-v1\|Governance Pack Design v1]]
- [[pwin-platform/skills/agent5-content-drafting/docs/governance-pack-page-design-workbook\|Governance Pack Page Workbook]]
- [[pwin-platform/test/skill-tests/README\|Skill Test Suite]]
- [[pwin-platform/test/skill-tests/WORKFLOW\|Test Workflow]]

---

## Project Decisions & Session History

These are in [[docs/context/MEMORY|MEMORY.md]] (auto-memory index). Key threads:

### Design Sessions
- [[docs/context/project_session_submissions_redesign\|Session 8: Submissions Redesign]]
- [[docs/context/project_session_scheduling_design\|Session 9: Scheduling]]
- [[docs/context/project_session10_ux_review\|Session 10: UX Review]]
- [[docs/context/project_session11_gold_standard\|Session 11: Gold Standard]]
- [[docs/context/project_session12_notes\|Session 12: Mapping]]
- [[docs/context/project_session13_ai_use_cases\|Session 13: AI Use Cases]]
- [[docs/context/project_session14_agents\|Session 14: Agents]]
- [[docs/context/project_session15_multiproduct\|Session 15: Multi-Product]]
- [[docs/context/project_session16_mcp_build\|Session 16: MCP Build]]

### Architecture & Strategy
- [[docs/context/project_methodology_data_model\|Methodology Data Model]]
- [[docs/context/project_ai_value_layers\|Four-Layer AI Value]]
- [[docs/context/project_evaluation_strategy_module\|Evaluation & Win Strategy Module]]
- [[docs/context/project_sol_archetypes\|SOL Workstream Archetypes]]
- [[docs/context/project_skill_workflow_design\|Skill Workflow Engine]]
- [[docs/context/project_governance_pack_design\|Governance Pack Design]]
- [[docs/context/project_competitor_profiling_redesign\|Competitor Profiling Redesign]]
- [[docs/context/project_intelligence_output_format\|Intelligence Output Format]]
- [[docs/context/project_agent_skill_allocation\|Agent Skill Allocation]]

### Commercial & Product
- [[docs/context/project_bid_forensics_service\|Bid Forensics Service]]
- [[docs/context/project_client_onboarding\|Client Onboarding]]
- [[docs/context/project_api_cost_analysis\|API Cost Analysis]]
- [[docs/context/project_qualify_priority\|Qualify is #1 Priority]]
- [[docs/context/project_competitive_intel_build\|Competitive Intel Build]]

### Feedback & Principles
- [[docs/context/feedback_persona_pattern\|Persona Pattern (Alex Mercer)]]
- [[docs/context/feedback_scope_discipline\|Scope Discipline]]
- [[docs/context/feedback_output_format\|Output Format]]
- [[docs/context/feedback_skill_depth\|Skills Need Domain Depth]]
- [[docs/context/feedback_qualify_lead_gen_scope\|Qualify Lead Gen Scope]]
- [[docs/context/user_profile\|User Profile]]
