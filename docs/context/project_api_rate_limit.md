---
name: API rate limit upgrade pending
description: 2026-04-04 — currently Tier 1 (30K input tokens/min). User contacting Anthropic to increase. Design for Tier 3 (120K/min) as production baseline. Remove conservative delays once upgraded.
type: project
---

## API Rate Limit

### Current state
- Tier 1: 30K input tokens/minute (new account default)
- Workaround: 2-second inter-turn delays + retry with 30s/60s backoff in skill-runner.js
- Works for testing but adds latency

### Action
- User is contacting Anthropic to request rate limit increase
- Target: Tier 3 (120K/min) as production baseline — requires ~$200 cumulative spend
- Once upgraded: remove conservative delays from skill runner, design skill orchestration for 120K/min throughput

### How to apply
When rate limit is confirmed upgraded, update skill-runner.js: remove the 2-second inter-turn delay and reduce backoff timers. The retry logic should stay as a safety net but the default path should assume sufficient headroom.
