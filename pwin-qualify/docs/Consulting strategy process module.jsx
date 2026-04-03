import { useState } from "react";

const STEPS = [
  {
    id: 1,
    code: "S1",
    title: "Data Collection & Input",
    subtitle: "Bid team gathers and inputs intelligence",
    type: "process",
    color: "#3b82f6",
    darkColor: "#1d4ed8",
    bg: "#0f172a",
    icon: "◈",
    owner: "Bid Team",
    reviewer: "Commercial Lead / Bid Manager",
    duration: "1–3 days",
    details: {
      what: "Bid team collects and inputs all available intelligence against the Phase 1 proforma: procurement documents, competitive intelligence, client context, financial data, solution context, and legal/compliance data.",
      inputs: ["ITT / Contract Notice", "Competitive intelligence", "Client strategy documents", "BIP credentials & CVs", "Financial data (rate card, past margins)", "Legal/compliance documents"],
      outputs: ["Completed Phase 1 data input form", "Source references for each data point", "Confidence ratings selected by user", "Intelligence gaps flagged"],
      roles: [
        { role: "Bid Manager", responsibility: "Owns the data collection process. Ensures all mandatory fields are completed before submission." },
        { role: "Account Lead", responsibility: "Provides client intelligence and relationship map. Confirms relationship warmth ratings." },
        { role: "Commercial Lead", responsibility: "Inputs financial data: revenue estimate, cost build, margin calculation, sensitivity scenarios." },
        { role: "Legal / Commercial", responsibility: "Reviews draft contract terms. Identifies deviations and compliance requirements." },
        { role: "Delivery Lead", responsibility: "Inputs resource plan, capability assessment, technology dependencies, delivery risks." },
      ],
      risks: [
        { level: "CRITICAL", risk: "Optimism bias at input", detail: "Bid team inputs most favourable interpretation of ambiguous intelligence. Root risk — all downstream analysis depends on input quality." },
        { level: "HIGH", risk: "Incomplete fields bypassed", detail: "Users skip fields where data is weak rather than flagging as Unknown. System must enforce confidence rating selection — cannot be blank." },
        { level: "HIGH", risk: "Relationship overstatement", detail: "Relationships described as warmer than evidence supports. Requires named contacts, dated interactions — not qualitative descriptions." },
        { level: "MEDIUM", risk: "Financial data not bottom-up", detail: "Cost estimated from margin target rather than built from resource plan. System should require itemised cost build." },
      ],
      checks: [
        "System enforces confidence rating (H/M/L/U) on every field — cannot be left blank",
        "Mandatory fields flagged red until completed",
        "Named sources required for High confidence ratings",
        "Completeness score calculated in real time — minimum 60% to proceed",
        "Second reviewer (independent of pursuit) reviews inputs before AI processing",
      ],
      mitigations: "Consider requiring a second person — independent of the pursuit team — to review data inputs before Step 2 begins. A commercial lead or bid manager reviewing completeness and honesty of inputs before AI processing would significantly reduce optimism bias.",
    }
  },
  {
    id: "G1",
    code: "G1",
    title: "GATE 1",
    subtitle: "Intelligence Brief Quality Gate",
    type: "gate",
    color: "#f59e0b",
    darkColor: "#b45309",
    bg: "#1c0f00",
    icon: "◆",
    owner: "Independent Reviewer",
    reviewer: "Commercial Director / Bid Quality Lead",
    duration: "2–4 hours",
    details: {
      what: "Formal gate review. An independent reviewer — not the pursuit team — assesses whether the intelligence brief is complete and honest enough to support rigorous qualification. This is a quality gate, not a pursuit decision.",
      inputs: ["Completed Phase 1 data input form", "Completeness score from system", "Confidence rating summary", "Intelligence gaps register"],
      outputs: ["Gate 1 PASS: proceed to AI processing", "Gate 1 REFER BACK: specific gaps to resolve", "Gate 1 ESCALATE: fatal flaw identified requiring Partner review"],
      roles: [
        { role: "Independent Reviewer", responsibility: "Reviews completeness and honesty of inputs. Must be independent of the pursuit team. Does NOT assess whether the opportunity is good — only whether the brief is complete." },
        { role: "Commercial Director", responsibility: "Signs off Gate 1 pass. Accountable for brief quality before AI processing begins." },
      ],
      risks: [
        { level: "CRITICAL", risk: "Reviewer is part of pursuit team", detail: "If the Gate 1 reviewer wants the bid to proceed, they will apply a lenient standard. Independence at this gate is non-negotiable." },
        { level: "HIGH", risk: "Maturity assessed subjectively", detail: "Without a defined checklist, 'mature' means different things to different reviewers. Use the five-condition checklist — not a judgement call." },
      ],
      checks: [
        "Completeness score ≥ 60% (system-calculated)",
        "No CRITICAL fields rated Unknown",
        "No unaddressed fatal flaws",
        "Minimum 2 sources per section",
        "All confidence ratings reviewed and accepted or challenged by reviewer",
        "Reviewer is confirmed independent of pursuit team",
      ],
      mitigations: "Gate 1 reviewer should be a named role — not whoever is available. Consider a rota of commercial directors or senior bid managers who rotate across pursuits to maintain independence.",
    }
  },
  {
    id: 2,
    code: "S2",
    title: "AI Report Generation",
    subtitle: "AI processes intelligence and generates Phase 1 brief",
    type: "process",
    color: "#8b5cf6",
    darkColor: "#6d28d9",
    bg: "#0f0a1e",
    icon: "◉",
    owner: "AI System",
    reviewer: "Bid Manager (human review)",
    duration: "Automated (minutes)",
    details: {
      what: "The AI processes all ingested data against the Phase 1 plugin Skill. It applies reasoning rules, populates the Template Schema, generates the opportunity narrative, produces an initial pWin indicator, and identifies any fatal flaws or critical gaps.",
      inputs: ["Gate 1 approved intelligence brief", "Phase 1 Skill (reasoning rules)", "Template Schema", "BIP knowledge base (credentials, past bids)"],
      outputs: ["Populated Template — all 57 fields", "Opportunity narrative (3 paragraphs)", "Initial pWin indicator with reasoning", "Fatal flaw register", "Intelligence gap register", "Phase 2 readiness assessment"],
      roles: [
        { role: "AI System", responsibility: "Applies all reasoning rules. Populates Template Schema. Generates narrative synthesis. Calculates pWin. Flags all fatal flaws and CRITICAL gaps." },
        { role: "Bid Manager", responsibility: "Conducts human-in-the-loop review of AI output. Assesses document maturity against defined checklist. Does not modify AI conclusions — flags disagreements for record." },
      ],
      risks: [
        { level: "HIGH", risk: "Hallucinated intelligence", detail: "AI presents inferred data as confirmed fact. System must clearly label every output as Confirmed / Inferred / Unknown — never silently presented as fact." },
        { level: "HIGH", risk: "Subjective maturity assessment", detail: "Human reviewer applies inconsistent standard without a defined checklist. Maturity must be defined as a pass/fail checklist, not a judgement." },
        { level: "MEDIUM", risk: "Reasoning rules not matched to context", detail: "Generic rules produce generic output. BIP-specific rules encoding actual bid expertise are required — designed in the proforma workshop." },
      ],
      checks: [
        "All AI outputs clearly labelled: Confirmed / Inferred / Unknown",
        "Every conclusion links to source data point (audit trail)",
        "Fatal flaws prominently displayed — cannot be buried in body of report",
        "pWin figure shows explicit weighted reasoning — not a black box number",
        "Bid Manager reviews against 5-condition maturity checklist",
        "Any AI conclusion the reviewer disagrees with must be logged with counter-evidence",
      ],
      mitigations: "Human reviewer's role is quality assurance only — not moderation of uncomfortable findings. The reviewer confirms the AI has applied the rules correctly, not that they agree with the conclusions.",
    }
  },
  {
    id: 3,
    code: "S3",
    title: "Question Generation & Validation",
    subtitle: "AI generates interrogation questions. Human validates.",
    type: "process",
    color: "#ec4899",
    darkColor: "#be185d",
    bg: "#1a0a12",
    icon: "◇",
    owner: "AI System + Validator",
    reviewer: "Senior Bid Director (independent)",
    duration: "Half day",
    details: {
      what: "Using the Phase 1 brief and the selected executive persona(s), the AI generates a targeted set of interrogation questions. Questions are designed to probe weak areas, test the accuracy of stated positions, and surface hidden risks. A human validator reviews the question set before the interrogation begins.",
      inputs: ["Approved Phase 1 brief", "Selected executive persona (CEO / CFO / Bid Director)", "Fatal flaw register", "Intelligence gap register"],
      outputs: ["Validated question set per persona", "Question areas (shared with bid team pre-interrogation)", "Specific questions (withheld until Step 4)", "Removed question log (audit trail)"],
      roles: [
        { role: "AI System", responsibility: "Generates questions targeting: weak confidence ratings, fatal flaw areas, intelligence gaps, areas where stated position is inconsistent with known facts from Phase 1 brief." },
        { role: "Senior Bid Director", responsibility: "Validates question relevance and technical accuracy. DOES NOT remove uncomfortable questions. Documents any removals with rationale. Must be independent of pursuit." },
        { role: "Pursuit Partner", responsibility: "NOT involved in question validation. Prevents softening of question set by pursuit-interested parties." },
      ],
      risks: [
        { level: "CRITICAL", risk: "Questions softened at validation", detail: "Validator removes difficult questions to protect the team. Converts interrogation into a test the team can pass. Any removal must be documented with named rationale." },
        { level: "HIGH", risk: "Validator is pursuit-interested", detail: "If the validator wants the bid to proceed, they will moderate the question list. Must be independent — ideally a bid director from a different practice." },
        { level: "MEDIUM", risk: "Team sees specific questions in advance", detail: "Allows rehearsed answers rather than honest responses. Share question areas (topics) not specific questions before Step 4." },
        { level: "MEDIUM", risk: "Fatal flaw questions removed", detail: "A question targeting a fatal flaw must require named sign-off above bid team level to remove. Cannot be removed without audit record." },
      ],
      checks: [
        "Validator confirmed independent of pursuit team",
        "Every question removal documented with: question text, reason for removal, name of person who approved removal",
        "Fatal flaw questions: removal requires Partner sign-off — logged in audit trail",
        "Question areas (not specific questions) shared with bid team 24 hours before Step 4",
        "Minimum question count per persona: 8–12 questions",
        "Questions reviewed for technical accuracy only — not for difficulty level",
      ],
      mitigations: "The validator's mandate must be explicitly stated: confirm questions are relevant and accurate. It is not their job to make the interrogation comfortable. Frame this explicitly in the process governance.",
    }
  },
  {
    id: 4,
    code: "S4",
    title: "Bid Team Interrogation",
    subtitle: "Executive personas question the bid team",
    type: "process",
    color: "#f97316",
    darkColor: "#c2410c",
    bg: "#1a0d00",
    icon: "◑",
    owner: "Bid Team (answering)",
    reviewer: "AI System (evaluating)",
    duration: "2–4 hours",
    details: {
      what: "The bid team is put through a structured interrogation by the AI acting as defined executive personas (CEO, CFO, Bid Director). Team members provide direct answers to qualification questions. The AI probes answers, identifies inconsistencies, and flags evasive or unsupported responses.",
      inputs: ["Validated question set", "Phase 1 brief (AI context)", "Individual team member responses"],
      outputs: ["Full interrogation transcript", "Answer quality assessment", "Cross-team consistency analysis", "Counter-evidence log", "Updated risk register"],
      roles: [
        { role: "Individual Bid Team Members", responsibility: "Answer questions individually and honestly. Provide specific, evidenced responses. Can provide counter-evidence to AI assessments but must be specific and sourced." },
        { role: "AI System (Persona)", responsibility: "Conducts structured interrogation. Probes answers that are vague, evasive, or inconsistent with Phase 1 brief. Flags short or unsupported responses. Identifies cross-team inconsistencies." },
        { role: "Bid Manager", responsibility: "Facilitates the session. Does not answer questions on behalf of team members. Ensures process is followed." },
        { role: "Pursuit Partner", responsibility: "Participates as a team member — does NOT lead or direct team answers. Social hierarchy must not override honest individual responses." },
      ],
      risks: [
        { level: "CRITICAL", risk: "Group dynamics override honest answers", detail: "Junior members defer to partner's optimistic position in a group session. Consider individual responses with cross-team consistency checking rather than group interrogation." },
        { level: "HIGH", risk: "Evasive or rehearsed answers", detail: "Short, defensive responses that restate the question. System should flag responses below word threshold and prompt for substantive input before proceeding." },
        { level: "HIGH", risk: "Counter-evidence accepted without scrutiny", detail: "Team disagrees with AI assessment but provides assertion rather than evidence. Counter-evidence must be specific and sourced — not 'we know our relationships are strong'." },
        { level: "MEDIUM", risk: "One person dominates responses", detail: "Bid lead answers all questions — removes individual perspective. Assign specific questions to specific roles. Each person answers within their domain." },
        { level: "MEDIUM", risk: "Time pressure produces low quality responses", detail: "If team is busy, Step 4 becomes a box-ticking exercise. Block time in advance. Treat as a formal governance event, not an admin task." },
      ],
      checks: [
        "Individual responses collected independently before any group discussion",
        "Cross-team consistency analysis: AI flags where two team members gave contradictory answers",
        "Response quality gate: AI flags responses below 50 words or that restate the question",
        "Counter-evidence requirement: disagreement with AI assessment requires specific named source",
        "Pursuit Partner participates as team member only — no facilitation role",
        "Full transcript preserved for audit trail",
        "All counter-evidence and disputes logged — not silently accepted",
      ],
      mitigations: "Strongly recommend individual digital responses (not a group verbal session) collected asynchronously. The AI then analyses cross-team consistency. Group dynamics cannot distort individual written responses. The interrogation output is richer and more honest.",
    }
  },
  {
    id: 5,
    code: "S5",
    title: "Evaluation Report & pWin",
    subtitle: "AI generates bid evaluation with persona-level guidance",
    type: "process",
    color: "#10b981",
    darkColor: "#047857",
    bg: "#001a10",
    icon: "◐",
    owner: "AI System",
    reviewer: "Commercial Director",
    duration: "Automated + 2hr review",
    details: {
      what: "The AI synthesises the complete picture — Phase 1 brief, interrogation transcript, counter-evidence, consistency analysis — and produces a structured evaluation report. The report includes a transparent pWin calculation, persona-level executive feedback, and a prioritised action plan with pWin consequences attached to each item.",
      inputs: ["Approved Phase 1 brief", "Full interrogation transcript", "Counter-evidence log", "Cross-team consistency analysis"],
      outputs: ["pWin figure with weighted reasoning", "Executive summary per persona (CEO/CFO/Bid Director)", "Prioritised action plan with pWin consequences", "Go / Conditional Go / No Bid recommendation", "Formal bid evaluation report (PDF)"],
      roles: [
        { role: "AI System", responsibility: "Synthesises all inputs. Calculates pWin with transparent weighted reasoning. Generates persona-level feedback. Produces prioritised action plan. Generates formal report." },
        { role: "Commercial Director", responsibility: "Reviews report before Gate 2. Confirms pWin reasoning is sound. Checks action plan is specific and achievable. Does not modify — can flag for Gate 2 discussion." },
      ],
      risks: [
        { level: "HIGH", risk: "pWin figure challenged and dismissed", detail: "Experienced people distrust model outputs. pWin must show explicit weighted logic — each dimension scored, weighted, with narrative reasoning. Make it arguable, not opaque." },
        { level: "HIGH", risk: "Action plan without consequences", detail: "List of things to improve with no priority or pWin impact. Every action must state: what, by when, and what happens to pWin if not done. Actions without consequences are ignored." },
        { level: "MEDIUM", risk: "Report informs but does not govern", detail: "Report sits in a folder while bid continues regardless. Without Gate 2, the process generates insight but does not change behaviour." },
        { level: "MEDIUM", risk: "Persona feedback conflicts with each other", detail: "CFO and CEO give contradictory recommendations. Report must reconcile conflicts explicitly — not leave the reader to arbitrate between personas." },
      ],
      checks: [
        "pWin figure shows: dimension scores, weightings, narrative reasoning for each — full audit trail",
        "Every action item states: what specifically, by when, pWin impact if not done",
        "Actions ranked by pWin impact — not by ease of resolution",
        "Persona-level sections clearly separated: CEO view, CFO view, Bid Director view",
        "Conflicting persona recommendations reconciled with explicit reasoning",
        "Report reviewed by Commercial Director before Gate 2",
        "Report formatted for board presentation — executive readable in 3 minutes",
      ],
      mitigations: "The pWin number will be challenged. Design the report so that challenging the number means engaging with the reasoning — not dismissing the output. Transparent logic converts sceptics into participants in the analysis.",
    }
  },
  {
    id: "G2",
    code: "G2",
    title: "GATE 2",
    subtitle: "Formal Go / No-Go Decision",
    type: "gate",
    color: "#ef4444",
    darkColor: "#b91c1c",
    bg: "#1a0000",
    icon: "◆",
    owner: "Pursuit Board / Partner",
    reviewer: "Managing Partner / Practice Lead",
    duration: "1–2 hours",
    details: {
      what: "Formal pursuit board meeting. The evaluation report is presented to accountable decision-makers. A Go / Conditional Go / No Bid decision is made and recorded with rationale. If Conditional Go, specific conditions and owners are documented. This is where authority sits — not in the team.",
      inputs: ["Evaluation report and pWin", "Action plan with pWin consequences", "Gate 1 record", "Commercial Director review notes"],
      outputs: ["Formal go/no-go decision (recorded)", "If Conditional Go: conditions list with owner and deadline for each", "If No Bid: reason recorded and pursuit stood down", "Bid investment authorisation (if Go)"],
      roles: [
        { role: "Managing Partner / Practice Lead", responsibility: "Chairs Gate 2. Makes final go/no-go decision. Accountable for the pursuit investment decision. Signs off any below-threshold margin exceptions." },
        { role: "Commercial Director", responsibility: "Presents evaluation report. Confirms commercial viability of the bid investment. Recommends decision based on report findings." },
        { role: "Pursuit Partner", responsibility: "Presents the opportunity case. Does NOT chair or facilitate — removes conflict of interest from the decision." },
        { role: "Bid Manager", responsibility: "Records the decision, conditions, and owners. Produces audit record of the Gate 2 outcome." },
      ],
      risks: [
        { level: "CRITICAL", risk: "No formal decision recorded", detail: "Meeting happens but outcome is informal. Without a recorded decision with accountability attached, the process does not change behaviour." },
        { level: "HIGH", risk: "Pursuit partner chairs the gate", detail: "Person with most to gain from a Go decision controls the process. Chair must be independent — practice lead or managing partner." },
        { level: "HIGH", risk: "Conditions on Conditional Go are vague", detail: "Conditional Go without specific, owned, time-bound conditions is effectively an unconditional Go. Each condition must have a named owner and a deadline." },
        { level: "MEDIUM", risk: "No Bid decision not enforced", detail: "Team continues to work on the bid informally after a No Bid decision. No Bid must result in formal stand-down with resource reallocation." },
      ],
      checks: [
        "Decision recorded in writing: Go / Conditional Go / No Bid with rationale",
        "Chair confirmed as independent of pursuit team",
        "All attendees named and recorded",
        "Conditional Go: each condition has a named owner, specific deliverable, and deadline",
        "No Bid: formal stand-down issued — bid resource reallocated",
        "Bid investment authorisation issued for Go decisions — connects pursuit decision to resource commitment",
        "Gate 2 record stored with Gate 1 record and evaluation report for audit",
      ],
      mitigations: "Gate 2 is where the process either changes behaviour or it does not. A recorded decision with named accountability is the difference between a qualification tool and a qualification theatre.",
    }
  },
];

const LEGEND = [
  { color: "#3b82f6", label: "Process Step" },
  { color: "#f59e0b", label: "Quality Gate" },
  { color: "#10b981", label: "Human-in-the-Loop" },
  { color: "#ef4444", label: "Critical Risk" },
  { color: "#f97316", label: "High Risk" },
];

const RISK_COLORS = { CRITICAL: "#ef4444", HIGH: "#f97316", MEDIUM: "#f59e0b", LOW: "#10b981" };

export default function ProcessDiagram() {
  const [selected, setSelected] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  const step = selected !== null ? STEPS.find(s => s.id === selected) : null;

  return (
    <div style={{ minHeight: "100vh", background: "#070d1a", fontFamily: "'Georgia', serif", color: "#e2e8f0" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300&family=DM+Mono:wght@300;400&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 2px; }
        .step-node { transition: all 0.2s ease; cursor: pointer; }
        .step-node:hover { transform: translateY(-2px); }
        .tab-btn { transition: all 0.2s; border: none; cursor: pointer; font-family: 'DM Mono', monospace; }
        .tab-btn:hover { opacity: 0.8; }
        .risk-badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 9px; font-family: 'DM Mono', monospace; font-weight: 600; letter-spacing: 1px; }
      `}</style>

      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #0d1b3e 0%, #0f172a 100%)", borderBottom: "1px solid #1e293b", padding: "20px 32px" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontSize: 10, letterSpacing: 4, color: "#3b82f6", textTransform: "uppercase", marginBottom: 4, fontFamily: "'DM Mono', monospace" }}>BIP Consulting · AI Bid Intelligence Platform</div>
            <h1 style={{ fontSize: 22, fontFamily: "'Crimson Pro', serif", fontWeight: 300, color: "#f0f4ff", margin: 0, letterSpacing: 0.5 }}>Phase 1–5 Qualification Process</h1>
            <div style={{ fontSize: 11, color: "#64748b", marginTop: 3, fontFamily: "'DM Mono', monospace" }}>With governance gates, roles, responsibilities & risk controls</div>
          </div>
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            {LEGEND.map(l => (
              <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 10, height: 10, borderRadius: l.label.includes("Gate") ? 0 : "50%", background: l.color, transform: l.label.includes("Gate") ? "rotate(45deg)" : "none" }} />
                <span style={{ fontSize: 10, color: "#64748b", fontFamily: "'DM Mono', monospace" }}>{l.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "28px 32px", display: "grid", gridTemplateColumns: selected ? "1fr 420px" : "1fr", gap: 24 }}>

        {/* Process Flow */}
        <div>
          {/* Flow instruction */}
          <div style={{ marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ height: 1, flex: 1, background: "linear-gradient(90deg, #1e293b, transparent)" }} />
            <span style={{ fontSize: 10, color: "#334155", fontFamily: "'DM Mono', monospace", letterSpacing: 2 }}>CLICK ANY STEP FOR FULL DETAIL</span>
            <div style={{ height: 1, flex: 1, background: "linear-gradient(270deg, #1e293b, transparent)" }} />
          </div>

          {/* Steps */}
          <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
            {STEPS.map((s, idx) => {
              const isGate = s.type === "gate";
              const isSelected = selected === s.id;
              return (
                <div key={s.id}>
                  <div
                    className="step-node"
                    onClick={() => { setSelected(isSelected ? null : s.id); setActiveTab("overview"); }}
                    style={{
                      background: isSelected ? s.bg : "#0d1525",
                      border: `1px solid ${isSelected ? s.color : "#1e293b"}`,
                      borderRadius: isGate ? 4 : 10,
                      padding: isGate ? "14px 24px" : "20px 24px",
                      display: "grid",
                      gridTemplateColumns: "52px 1fr auto",
                      gap: 16,
                      alignItems: "center",
                      position: "relative",
                      overflow: "hidden",
                    }}>

                    {/* Left accent */}
                    <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: isSelected ? s.color : (isGate ? s.color + "60" : s.color + "40") }} />

                    {/* Icon/badge */}
                    <div style={{ textAlign: "center" }}>
                      {isGate ? (
                        <div style={{ width: 36, height: 36, background: s.color + "20", border: `2px solid ${s.color}`, transform: "rotate(45deg)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto" }}>
                          <span style={{ transform: "rotate(-45deg)", fontSize: 14, color: s.color, display: "block" }}>◆</span>
                        </div>
                      ) : (
                        <div style={{ width: 40, height: 40, borderRadius: "50%", background: s.color + "15", border: `1.5px solid ${s.color}40`, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto" }}>
                          <span style={{ fontSize: 18, color: s.color }}>{s.icon}</span>
                        </div>
                      )}
                      <div style={{ fontSize: 9, color: s.color, fontFamily: "'DM Mono', monospace", marginTop: 4, letterSpacing: 1 }}>{s.code}</div>
                    </div>

                    {/* Content */}
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 3 }}>
                        <span style={{ fontSize: isGate ? 12 : 14, fontFamily: "'Crimson Pro', serif", color: isSelected ? "#f0f4ff" : "#cbd5e1", fontWeight: isGate ? 600 : 400, letterSpacing: isGate ? 2 : 0, textTransform: isGate ? "uppercase" : "none" }}>{s.title}</span>
                        {isGate && <div style={{ height: 1, flex: 1, background: s.color + "30" }} />}
                      </div>
                      <div style={{ fontSize: 11, color: "#64748b", fontFamily: "'DM Mono', monospace" }}>{s.subtitle}</div>
                      {!isGate && (
                        <div style={{ display: "flex", gap: 16, marginTop: 8 }}>
                          <span style={{ fontSize: 10, color: "#475569", fontFamily: "'DM Mono', monospace" }}>Owner: <span style={{ color: s.color + "cc" }}>{s.owner}</span></span>
                          <span style={{ fontSize: 10, color: "#475569", fontFamily: "'DM Mono', monospace" }}>Duration: <span style={{ color: "#94a3b8" }}>{s.duration}</span></span>
                        </div>
                      )}
                    </div>

                    {/* Risk summary */}
                    <div style={{ display: "flex", flexDirection: "column", gap: 4, alignItems: "flex-end" }}>
                      {s.details.risks.slice(0, 2).map((r, i) => (
                        <div key={i} className="risk-badge" style={{ background: RISK_COLORS[r.level] + "20", color: RISK_COLORS[r.level], border: `1px solid ${RISK_COLORS[r.level]}40` }}>
                          {r.level}
                        </div>
                      ))}
                      <div style={{ fontSize: 10, color: "#334155", fontFamily: "'DM Mono', monospace", marginTop: 2 }}>
                        {s.details.risks.length} risk{s.details.risks.length !== 1 ? "s" : ""}
                      </div>
                    </div>
                  </div>

                  {/* Connector */}
                  {idx < STEPS.length - 1 && (
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "2px 0", position: "relative" }}>
                      <div style={{ width: 1, height: 20, background: "linear-gradient(180deg, #1e3a5f, #334155)" }} />
                      <div style={{ position: "absolute", fontSize: 10, color: "#1e3a5f" }}>▼</div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Summary bar */}
          <div style={{ marginTop: 28, background: "#0d1525", border: "1px solid #1e293b", borderRadius: 8, padding: "16px 24px", display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16 }}>
            {[
              { label: "Total Steps", value: "5 + 2 Gates", color: "#3b82f6" },
              { label: "Human Checkpoints", value: "6 Reviews", color: "#10b981" },
              { label: "Critical Risks", value: STEPS.reduce((a,s) => a + s.details.risks.filter(r=>r.level==="CRITICAL").length, 0), color: "#ef4444" },
              { label: "High Risks", value: STEPS.reduce((a,s) => a + s.details.risks.filter(r=>r.level==="HIGH").length, 0), color: "#f97316" },
            ].map(item => (
              <div key={item.label} style={{ textAlign: "center" }}>
                <div style={{ fontSize: 22, color: item.color, fontFamily: "'Crimson Pro', serif", fontWeight: 300 }}>{item.value}</div>
                <div style={{ fontSize: 10, color: "#475569", fontFamily: "'DM Mono', monospace", letterSpacing: 1, textTransform: "uppercase", marginTop: 2 }}>{item.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Detail Panel */}
        {step && (
          <div style={{ position: "sticky", top: 20, height: "fit-content", maxHeight: "90vh", overflowY: "auto" }}>
            <div style={{ background: "#0d1525", border: `1px solid ${step.color}40`, borderRadius: 10, overflow: "hidden" }}>

              {/* Panel header */}
              <div style={{ background: step.bg, borderBottom: `1px solid ${step.color}30`, padding: "16px 20px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ fontSize: 9, color: step.color, letterSpacing: 3, fontFamily: "'DM Mono', monospace", textTransform: "uppercase", marginBottom: 4 }}>{step.code} · {step.type === "gate" ? "GOVERNANCE GATE" : "PROCESS STEP"}</div>
                    <div style={{ fontSize: 16, fontFamily: "'Crimson Pro', serif", color: "#f0f4ff", fontWeight: 300 }}>{step.title}</div>
                    <div style={{ fontSize: 11, color: "#64748b", fontFamily: "'DM Mono', monospace", marginTop: 2 }}>{step.subtitle}</div>
                  </div>
                  <button onClick={() => setSelected(null)} style={{ background: "none", border: "none", color: "#475569", cursor: "pointer", fontSize: 18, padding: 0, lineHeight: 1 }}>×</button>
                </div>
                <div style={{ display: "flex", gap: 12, marginTop: 10 }}>
                  <span style={{ fontSize: 10, color: "#475569", fontFamily: "'DM Mono', monospace" }}>Owner: <span style={{ color: step.color + "cc" }}>{step.owner}</span></span>
                  {step.type !== "gate" && <span style={{ fontSize: 10, color: "#475569", fontFamily: "'DM Mono', monospace" }}>⏱ {step.duration}</span>}
                </div>
              </div>

              {/* Tabs */}
              <div style={{ display: "flex", borderBottom: "1px solid #1e293b" }}>
                {["overview","roles","risks","checks"].map(tab => (
                  <button key={tab} className="tab-btn" onClick={() => setActiveTab(tab)}
                    style={{ flex: 1, padding: "10px 6px", background: activeTab === tab ? step.color + "15" : "transparent", color: activeTab === tab ? step.color : "#475569", fontSize: 10, letterSpacing: 1, textTransform: "uppercase", borderBottom: activeTab === tab ? `2px solid ${step.color}` : "2px solid transparent" }}>
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              <div style={{ padding: "16px 20px" }}>

                {activeTab === "overview" && (
                  <div>
                    <p style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.7, margin: "0 0 16px" }}>{step.details.what}</p>

                    <div style={{ marginBottom: 14 }}>
                      <div style={{ fontSize: 9, color: step.color, letterSpacing: 2, fontFamily: "'DM Mono', monospace", textTransform: "uppercase", marginBottom: 8 }}>Inputs</div>
                      {step.details.inputs.map((inp, i) => (
                        <div key={i} style={{ fontSize: 11, color: "#64748b", padding: "4px 0", borderBottom: "1px solid #0f172a", display: "flex", gap: 8 }}>
                          <span style={{ color: "#1e3a5f" }}>→</span>{inp}
                        </div>
                      ))}
                    </div>

                    <div style={{ marginBottom: 14 }}>
                      <div style={{ fontSize: 9, color: step.color, letterSpacing: 2, fontFamily: "'DM Mono', monospace", textTransform: "uppercase", marginBottom: 8 }}>Outputs</div>
                      {step.details.outputs.map((out, i) => (
                        <div key={i} style={{ fontSize: 11, color: "#64748b", padding: "4px 0", borderBottom: "1px solid #0f172a", display: "flex", gap: 8 }}>
                          <span style={{ color: step.color + "60" }}>◈</span>{out}
                        </div>
                      ))}
                    </div>

                    {step.details.mitigations && (
                      <div style={{ background: step.color + "08", border: `1px solid ${step.color}20`, borderRadius: 6, padding: "12px 14px" }}>
                        <div style={{ fontSize: 9, color: step.color, letterSpacing: 2, fontFamily: "'DM Mono', monospace", textTransform: "uppercase", marginBottom: 6 }}>Design Recommendation</div>
                        <div style={{ fontSize: 11, color: "#94a3b8", lineHeight: 1.6 }}>{step.details.mitigations}</div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "roles" && (
                  <div>
                    {step.details.roles.map((r, i) => (
                      <div key={i} style={{ marginBottom: 12, padding: "12px 14px", background: "#070d1a", borderRadius: 6, borderLeft: `2px solid ${step.color}50` }}>
                        <div style={{ fontSize: 11, color: step.color, fontFamily: "'DM Mono', monospace", fontWeight: 500, marginBottom: 4 }}>{r.role}</div>
                        <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.6 }}>{r.responsibility}</div>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === "risks" && (
                  <div>
                    {step.details.risks.map((r, i) => (
                      <div key={i} style={{ marginBottom: 10, padding: "12px 14px", background: RISK_COLORS[r.level] + "08", border: `1px solid ${RISK_COLORS[r.level]}25`, borderRadius: 6 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
                          <span className="risk-badge" style={{ background: RISK_COLORS[r.level] + "20", color: RISK_COLORS[r.level], border: `1px solid ${RISK_COLORS[r.level]}40` }}>{r.level}</span>
                          <span style={{ fontSize: 11, color: "#cbd5e1", fontWeight: 600 }}>{r.risk}</span>
                        </div>
                        <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.6 }}>{r.detail}</div>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === "checks" && (
                  <div>
                    <div style={{ fontSize: 9, color: step.color, letterSpacing: 2, fontFamily: "'DM Mono', monospace", textTransform: "uppercase", marginBottom: 12 }}>Checks & Controls</div>
                    {step.details.checks.map((c, i) => (
                      <div key={i} style={{ display: "flex", gap: 10, alignItems: "flex-start", padding: "8px 0", borderBottom: "1px solid #0f172a" }}>
                        <div style={{ width: 18, height: 18, borderRadius: 3, background: step.color + "15", border: `1px solid ${step.color}40`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, marginTop: 1 }}>
                          <span style={{ fontSize: 8, color: step.color }}>✓</span>
                        </div>
                        <span style={{ fontSize: 11, color: "#64748b", lineHeight: 1.6 }}>{c}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {!selected && (
        <div style={{ maxWidth: 1200, margin: "0 auto", padding: "0 32px 32px" }}>
          <div style={{ background: "#0d1525", border: "1px solid #1e293b", borderRadius: 8, padding: "16px 24px" }}>
            <div style={{ fontSize: 9, color: "#3b82f6", letterSpacing: 3, fontFamily: "'DM Mono', monospace", textTransform: "uppercase", marginBottom: 10 }}>Key Design Principles</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16 }}>
              {[
                { icon: "◆", color: "#f59e0b", title: "Independence at Gates", text: "Gate reviewers must be independent of the pursuit team. Independence is non-negotiable — not a preference." },
                { icon: "◈", color: "#ef4444", title: "Optimism Bias is the Root Risk", text: "Everything downstream depends on input quality. The system must force specificity — named sources, dated contacts, explicit confidence ratings." },
                { icon: "◉", color: "#10b981", title: "Decisions Must Be Recorded", text: "Gate 2 without a recorded, accountable decision is process theatre. The report must connect to a governance moment." },
              ].map(p => (
                <div key={p.title} style={{ display: "flex", gap: 12 }}>
                  <span style={{ color: p.color, fontSize: 16, flexShrink: 0, marginTop: 2 }}>{p.icon}</span>
                  <div>
                    <div style={{ fontSize: 11, color: "#cbd5e1", fontFamily: "'DM Mono', monospace", marginBottom: 4 }}>{p.title}</div>
                    <div style={{ fontSize: 11, color: "#475569", lineHeight: 1.6 }}>{p.text}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
