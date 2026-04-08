---
name: Intelligence gathering skills are next priority after governance packs
description: 2026-04-06 — client profile and competitive intelligence skills needed to populate platform knowledge that enriches Qualify AI reviews
type: project
---

## Decision

After governance pack skill is complete, the next skill priorities are:

1. **Client profile skill** — builds structured profiles of government departments and public sector clients (procurement patterns, spending priorities, political dynamics, key decision-makers, known preferences)
2. **Competitive intelligence skill** — builds structured profiles of strategic suppliers (capabilities, sector focus, strengths/weaknesses, win/loss history, pricing reputation, reference sites)

## Why

The Qualify product AI quality is directly proportional to the context it receives. Currently it operates "cold" — it knows nothing about the bidder, client, or competitors beyond what the user types in. With pre-built intelligence profiles:

- AI reviews become dramatically more specific ("your last three bids against Capita in Defence were lost on price" vs generic "evidence doesn't name specific advantages")
- The free website tool stays as-is (self-service, user-provided context)
- The paid platform integrates the intelligence profiles for deeper analysis
- This is the commercial differentiator between the free tool and the paid product

## How to apply

1. Design the client profile skill (YAML config + output schema for markdown files)
2. Design the competitive intelligence skill (same pattern)
3. User schedules these skills to build profiles for: top 50 government strategic suppliers + all major government departments
4. Output markdown files stored in platform knowledge (or Google Drive initially)
5. When wired into the paid Qualify product, these files feed into the AI context block alongside the user's pursuit data

## Starting set (user to prioritise)

**Suppliers:** Serco, Capita, Sopra Steria, CGI, Atos, Fujitsu, DXC, Maximus, Mitie, G4S, Babcock, BAE Systems, Thales, Leidos, Raytheon, KPMG, Deloitte, PwC, EY, Accenture + 30 more
**Departments:** MOD, Home Office, MOJ, HMRC, DWP, NHS England, DHSC, Cabinet Office, DfE, DfT, Defra, FCDO + agencies
