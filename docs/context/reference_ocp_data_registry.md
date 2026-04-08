---
name: OCP Data Registry — canonical OCDS bulk source
description: Open Contracting Partnership Data Registry provides free weekly bulk downloads of UK FTS and other global OCDS feeds — check this before grinding any paginated OCDS API
type: reference
---

**Resource:** https://data.open-contracting.org — the Open Contracting Partnership Data Registry. Canonical index of all OCDS publishers worldwide, with weekly-refreshed bulk downloads in JSONL, CSV, and Excel formats.

**UK Find a Tender publication page:** https://data.open-contracting.org/en/publication/41

**Bulk download URLs (no auth, no rate limit):**
- All-time JSONL: `https://data.open-contracting.org/en/publication/41/download?name=full.jsonl.gz` (~200 MB gzipped, 5+ years)
- All-time CSV: `https://data.open-contracting.org/en/publication/41/download?name=full.csv.tar.gz`
- Yearly files also available

**Licence:** Open Government Licence v3.0 (UK data) — free for commercial use with attribution.

**What's in it:** OCDS "compiled" releases — one merged current-state record per contract OCID. Not release packages (individual update events). This means:
- Historical contract state (tender → award → contract) is collapsed into one record per OCID
- Forward-pipeline-only planning notices (notices where no tender has been issued yet) are NOT present as standalone records — for those, the live FTS API is the only source

**Data quality caveats (same as the source API):**
- Inconsistent OCIDs across releases
- Publishers often omit the identifier.scheme field, populating only identifier.id with a bare CH number — our extractor accommodates this as of c6ccbff
- Occasional date format errors, outlier values, foreign register numbers mis-tagged as GB-COH

**Why this matters as a reference:** In April 2026, before checking here first, we were about to grind 6+ hours through the paginated FTS API to backfill 2 years of history. The OCP bulk file gave us **5 years in 4 minutes**. The lesson: any time an OCDS publisher feed is slow or unreliable to backfill, check the OCP registry first. It covers most global publishers, not just the UK. Multi-publisher registries like this exist for many open-data domains — always check before building custom ingest infrastructure.
