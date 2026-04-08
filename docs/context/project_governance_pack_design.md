---
name: Governance pack skill design
description: Agent 5 governance pack skill — architecture decisions, three gate tiers, three content modes, platform knowledge pattern, reference documents analysed
type: project
---

Governance pack skill (agent5-content-drafting/governance-packs.yaml) redesigned from scaffold to production spec.

**Key decisions:**
- One skill, gate-tier-aware (not split into multiple skills)
- Three gate tiers: Qualification (small, Gates 0-2), Solution (medium, Gate 3), Submission (large, Gate 4), plus Contract delta (Gate 5)
- Three content modes per section: structured data (extract-and-place), contextual narrative (synthesis with preserved tone), visual reference (embed existing artefacts)
- Template knowledge extracted to platform knowledge files (4 JSON files), not embedded in skill YAML — enables client configuration
- Output format: HTML → PDF (landscape, slide-sized pages), not PowerPoint for V1
- Early gate value = better kill decisions via Qualify integration, not just time saving
- Late gate value = weeks compressed to days via automated assembly from structured workstream outputs

**Why:** Real governance packs (Capita CRC, Serco IC Gate 4) are sophisticated decision artefacts requiring structured data, contextual framing, and professional presentation. The skill must handle all three, not just data extraction.

**How to apply:** Design spec is at `pwin-platform/skills/agent5-content-drafting/docs/governance-pack-design-v1.md`. Build sequence: platform knowledge files → MCP tools → skill YAML rebuild → HTML template → test.

**Reference documents** in `pwin-platform/skills/agent5-content-drafting/reference/` — 5 PDFs from Capita and Serco covering real CRC/IC packs, templates, and governance methodology.
