---
name: Client scoring scheme is optional
description: Not all procurements have a client-disclosed marking scheme — low-value and commodity purchases rarely do. Never make it mandatory.
type: feedback
---

Client scoring scheme input must always be optional, never mandatory.

**Why:** Low-value procurements and transactional commodity purchases rarely have a client-disclosed marking scheme. Only complex/high-value ITTs typically include formal grade bands with descriptors and hurdle marks.

**How to apply:** When building UI for client scoring, always allow the bid manager to skip it entirely. No validation errors for missing scoring scheme. Quality self-assessment fields that depend on the scheme should gracefully degrade (hide or show "no scheme configured"). Same for review predicted client scores — optional column, not required.
