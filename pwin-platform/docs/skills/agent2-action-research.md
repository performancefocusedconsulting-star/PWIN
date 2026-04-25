# Skill design — `action-research`

**Agent:** 2 (Market & Competitive Intelligence)
**Status:** Design — not yet implemented
**Supersedes:** The Python `action_research` handler in `pwin-competitive-intel/agent/watcher.py`, which will be deleted once this skill is live.
**Owner:** Paul Fenton
**Last updated:** 2026-04-24

---

## 1. Purpose

Produce a disciplined fact-finding brief on a single pursuit that answers the questions Paul actually has in his head when he reads a new notice, so he can decide whether to invest further time and what kind of move to make.

## 2. Decision enabled

The brief exists to enable one of four follow-up decisions, in this order of preference:

1. **Commit** — pursue the opportunity (register, engage, start capture)
2. **Probe** — one specific follow-up question to resolve before deciding
3. **Hand off** — not a direct bid; potential content angle, intel product, or partner referral
4. **Pass** — not for us, log reason, close

If the brief doesn't make one of these four choices easier, it has failed.

## 3. Distinctive purpose — what this is NOT

- **Not the daily scan.** The daily scan scored this pursuit on three axes and decided it was worth surfacing. `research` does not re-score; it investigates.
- **Not the competitive analysis skill.** That skill builds supplier dossiers. `research` uses them.
- **Not a general "write me a brief."** Output is structured against seven lenses, each with defined data sources and explicit uncertainty handling.
- **Not content generation.** If the brief concludes there's a content angle, it hands off to `action-campaign`, which is a separate skill.

## 4. The seven lenses

Each lens is a required section of the output, answered against defined data sources with `[data]`, `[inferred]`, or `[unknown — requires lookup]` tags on every claim.

### Lens 1 — Orientation

**Question:** What is this, really?

**Outputs:**
- Buying entity (with parent / sponsoring department)
- Scope summary (one paragraph, factual)
- Estimated value + currency + VAT treatment
- Classification: greenfield new / extension / retender of existing / framework call-off
- Budget signal: is the value committed, indicative, or unstated?
- Policy backing: is there a named policy, White Paper, or ministerial commitment behind it?

**Data sources:**
- Notice body text (primary)
- `bid_intel.db.notices` for prior-year awards at this buyer in this category (classification signal)
- Manual list of named UK policies per domain (e.g. "Policing White Paper") — _not yet built_ ; flag as `[unknown]` for now

### Lens 2 — Buyer anomaly

**Question:** Why is *this* buyer releasing this, and not the buyer you'd expect?

**Outputs:**
- The buyer's usual spend pattern (top categories by award count and value, last 24 months)
- The category this notice falls into
- The typical buyer for that category across UK government
- Is there a mismatch? If yes, what does it suggest? (e.g. centralised procurement vehicle, policy-driven delegation, new commercial model)

**Data sources:**
- `bid_intel.db` buyer award history joined to CPV codes (we have this)
- A category-to-typical-buyer reference table — _not yet built_
- Reasoning over the mismatch — Claude, constrained

### Lens 3 — Inferred scope and implementation challenges

**Question:** What does the 3-line description actually imply, and what will be hard about delivering it?

**Outputs:**
- Decomposed requirements list (5–8 bullets): what the supplier will actually have to do
- Implementation challenges: 3–5 technical, operational, or political issues a delivery partner will face
- Supplier profile implied: what kind of organisation is this really for? (e.g. "large SI with public-safety practice + ability to broker an SME consortium")

**Data sources:**
- Notice text
- Claude reasoning (this is explicitly a generative step)
- Constraint: each challenge must state whether it is common across the category or specific to this notice

### Lens 4 — Timeline and procurement route

**Question:** When does what happen, and how might they actually buy this?

**Outputs:**
- Key dates: published, registration deadline, engagement session, tender expected, contract start, contract end
- Declared procurement route (if named in the notice)
- Candidate frameworks that *could* host this (named + reason why plausible)
- Does the named / candidate framework have live lots that match the scope? (Yes / No / Unknown)
- Notice lineage: is there a prior PIN or UK1 in the database for the same scope? If yes, what did it say and what's changed?

**Data sources:**
- Notice frontmatter (dates — we have)
- Notice text (declared route — we have)
- A UK frameworks table with current scope + call-off activity — _not yet built_, flag as `[unknown]`
- `bid_intel.db.notices` linkage by OCID prefix / buyer + keyword for prior-notice matching — possible today but imprecise

### Lens 5 — Engagement metadata (UK2 / UK1 only)

**Question:** If this is a market engagement, what are the mechanics?

**Outputs:**
- Format: in-person / virtual / hybrid
- Location (if in-person)
- Attendee restrictions (max attendees, eligibility requirements, NDA)
- Clarity of the ask: does the buyer say what they want to learn from the session? Rate as Clear / Vague / Unstated

**Data sources:**
- Notice text only
- Skip this lens entirely if `notice_type` is not UK1 or UK2

### Lens 6 — Consortium shape

**Question:** If this needs a team, what does the team look like?

**Outputs:**
- Is a consortium expected / encouraged / required / optional? (Based on notice text)
- Natural consortium shape: 2–4 role types needed (e.g. "prime systems integrator + AI assurance specialist + change management partner + SME/startup ecosystem partner")
- Named candidates per role, drawn only from award history for this buyer or similar — no invention
- Known contacts at any named candidate: reference `crm.db.contacts` — _currently empty_, flag with `[no contacts on file]`

**Data sources:**
- Notice text
- `bid_intel.db` buyer history + peer-buyer award history
- `crm.db.contacts` — returns nothing today, will light up as CRM fills

### Lens 7 — Tactical hook

**Question:** Is there a non-bid move worth making now?

**Outputs:**
- One sentence: is there a content angle / thought leadership move that could set the scene and position BidEquity before the ITT drops?
- If yes: one-line description of the angle
- Recommended handoff: `action-campaign` / none

**Data sources:**
- Synthesis of lenses 1–6
- No new data — this is a reasoning step only

---

## 5. Output structure

The skill produces a single markdown document, injected into the pursuit file under `## Research Brief`, replacing any existing brief.

Structure:

```markdown
## Research Brief
*Generated {datetime} · {notice ref}*

### 1. Orientation
...

### 2. Why this buyer?
...

### 3. Scope & implementation challenges
...

### 4. Timeline & route
...

### 5. Engagement details
(omitted — not a market engagement notice)

### 6. Consortium shape
...

### 7. Tactical hook
...

### Recommendation
One of: COMMIT · PROBE · HAND OFF · PASS
Followed by one sentence of rationale.

### Open questions for Paul
- Bulleted list of data gaps flagged `[unknown — requires lookup]` during the run
```

Every factual claim carries a `[data]`, `[inferred]`, or `[unknown]` tag.

## 6. Input context

The skill runner must gather, before calling Claude:

| Context key | Source | Status |
|---|---|---|
| `pursuit_file` | Obsidian markdown + frontmatter | ✅ have |
| `notice_text` | Notice description from `bid_intel.db.notices` | ✅ have |
| `buyer_history` | Awards + categories, last 24mo at this buyer | ✅ have (needs buyer-match fix first) |
| `peer_buyer_categories` | Other buyers who buy in the same CPV category | 🟡 query needs building |
| `frameworks_candidates` | Live frameworks matching scope | ❌ not yet — flag as unknown |
| `policy_references` | UK policy references by domain | ❌ not yet — flag as unknown |
| `prior_notices` | Prior PIN / UK1 on same scope | 🟡 possible with keyword match, imprecise |
| `crm_contacts` | Contacts at named candidate suppliers | ❌ empty table today |

Anything marked ❌ or 🟡 returns an empty structure; the skill must handle that gracefully by tagging `[unknown — requires lookup]` rather than fabricating.

## 7. Explicit constraints on the model

1. **No supplier name may appear in the brief unless it is in the data provided.** No drawing on general knowledge. If the data is thin, the consortium section says "No award history found — lens skipped."
2. **Every factual claim is tagged.** `[data]` for anything pulled from the DB or notice text. `[inferred]` for anything the model reasoned to. `[unknown]` for anything we asked for but couldn't provide.
3. **If a lens cannot be answered from the available data, say so explicitly.** Do not fill it with padding.
4. **Recommendation is one of four words.** COMMIT / PROBE / HAND OFF / PASS. Anything else fails the schema.
5. **Write for scan-reading.** Paul reads this in 60 seconds. Short paragraphs, bullets, no throat-clearing.

## 8. Success criteria

A brief is successful if:

1. Paul can make the Commit / Probe / Hand off / Pass decision from the brief alone without opening the notice.
2. Every specific claim (buyer name, supplier name, framework name, date, value) can be traced to a `[data]` tag and a real row in `bid_intel.db` or to the notice text.
3. Data gaps are surfaced, not hidden.
4. Reading time is under 90 seconds.

A brief has failed if:

1. It names specific suppliers that did not appear in the data.
2. It repeats content that was already in the daily scan digest or the pursuit file's existing body.
3. It hedges every recommendation into an unactionable "it depends."
4. It has more than 600 words.

## 9. Data and capability gaps

| Gap | Blocks which lens | Mitigation for v1 |
|---|---|---|
| Category → typical-buyer reference | 2 (buyer anomaly) | Hand-curated seed list of 20–30 common categories; expand over time |
| UK frameworks table with live scope | 4 (route) | Flag as `[unknown]` in v1; candidate for a separate ingest skill |
| Policy reference lookup | 1 (orientation) | Flag as `[unknown]` in v1; candidate for a manual seed list |
| Notice lineage / prior-PIN threading | 4 (route) | Best-effort keyword match in v1; proper threading is a separate platform task |
| `crm.db.contacts` empty | 6 (consortium) | Say "no contacts on file" in v1; fills naturally once Evaboot CSV imports start |
| Buyer-match misses composite buyer strings | All buyer-data lenses | Fix before v1 ships — hard dependency |

## 10. Out of scope for this skill

- Competitive analysis / supplier dossiers — separate skill
- Content drafting — `action-campaign`
- Outreach email drafting — `action-reach-out`
- Registration email drafting — `action-register`
- PWIN scoring — that's Qualify
- Win theme development — that's Agent 3

## 11. Open design questions

1. **Should the brief be regenerated if the notice is updated?** E.g. buyer releases a Q&A addendum. Today, once `processed_at` is set, the watcher skips the file. Option: add a `last_notice_update` field and re-fire if it's newer than `processed_at`.
2. **Does "Hand off" imply auto-triggering the downstream skill?** E.g. if Lens 7 says "yes, content angle," does the brief pre-fill the next action? Default: no, human always pulls the next trigger.
3. **Should the brief include a cost line?** E.g. "generated for £0.02, last 10 briefs cost £0.18". Useful for operational awareness if volume grows.
4. **Retention.** If Paul regenerates the brief, do we keep the prior version? Default: replace silently. Option: append under `## Research Brief (superseded)`.

---

## 12. Implementation plan (for when design is agreed)

1. Fix the buyer-match in `gather_buyer_context` — hard prerequisite for any live test
2. Build the category → typical-buyer seed reference (20–30 rows)
3. Write `pwin-platform/skills/agent2-market-competitive/action-research.yaml` from this spec
4. Wire the skill runner's context gatherers for `buyer_history`, `peer_buyer_categories`, `prior_notices`, `crm_contacts`
5. Refactor the watcher's `action_research` handler to call the platform skill instead of running Python locally
6. Delete the Python handler
7. Run live against BLC0329; iterate on the prompt until output passes success criteria
