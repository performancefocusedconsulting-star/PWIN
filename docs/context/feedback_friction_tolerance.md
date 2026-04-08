---
name: Spend small money to remove recurring friction
description: User's explicit preference — time spent babysitting broken infra is unacceptable even when technically "free"; small monthly costs to remove recurring friction are trivially worth it
type: feedback
---

When recommending infrastructure, runtime environments, or data sources, do NOT default to zero-cost options if they create recurring friction. The user's stated principle, verbatim:

> "I am in no rush for this but if it takes a week and its done and all the information is valid and correct then great — but spending 1-2 hours every day trying to fix this is getting annoying."

**Why:** Said in April 2026 after I proposed three zero-cost options for hosting a long-running backfill job (GitHub Actions, Codespace, local laptop), all of which had recurring friction. The user pushed back: "are you assuming I don't want to spend money so we are messing around on the fringes as opposed to getting it done?" The right answer was a £5/month VPS plus a free bulk data download — done in a session, zero babysitting.

**How to apply:**
- Time cost is real cost. A zero-cost option that requires 30 min of attention per week is worse than a £5/month option that requires zero attention.
- For infrastructure decisions, always surface a small-paid option alongside the free ones and explain the tradeoff honestly. Don't hide the paid option or frame it as "if you want to spend money".
- "Set and forget" is a legitimate optimisation target. If the user asks me to fix something that keeps breaking, don't just fix the immediate symptom — ask whether the underlying environment is the wrong place for this work.
- Willing to spend hundreds-to-low-thousands one-off for the right answer (e.g. buying historical bulk data from a vendor if it existed). The budget is proportionate to the value, not rigidly capped.
- This is NOT a blanket "always recommend paid" — free and open source are still preferred when they're not creating friction. The principle is about friction tolerance, not cost.
