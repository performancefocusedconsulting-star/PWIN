---
name: Module scope clarity — Submissions vs Reviews vs Governance
description: User corrected confusion between modules. Submissions = client requirements + production tracking. Reviews = formal peer/SME review of written responses. Governance = organisational assurance decisions.
type: feedback
---

The three assurance modules have distinct, non-overlapping scopes:

- **Submissions (M5):** Upload client requirements, track production lifecycle of each response, self-assess quality dimensions. This is about "what the client asked for" and "where are we with each response."
- **Reviews (M6):** Formal peer and external SME review of written responses at pink/red/gold stages. This is about "is the writing good enough" judged by independent reviewers.
- **Governance (M7):** Organisational assurance — solution, commercial/financial, and executive decisions. This is about "should we proceed" at an organisational level. Development reviews (solution, pricing, risk) belong here, not in Reviews.

**Why:** The original architecture blurred the line between these, putting development reviews in M6 alongside production reviews. The user clarified that development reviews are assurance decisions (Governance), not quality reviews of written content (Reviews).

**How to apply:** Never mix response quality review features with organisational governance features. When implementing, keep the three concerns clearly separated. Reviews are triggered by production lifecycle stages (pink_ready, red_ready, gold_ready) and their closure advances production status in Submissions.
