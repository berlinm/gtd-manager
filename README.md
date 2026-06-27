# GTD Manager

A personal web application for managing work according to the
[Getting Things Done](https://gettingthingsdone.com/) methodology.

## Overview

GTD Manager is a single-user, self-hosted application designed to run in
air-gapped environments. It provides a trusted system for capturing,
clarifying, organizing, and reviewing all your commitments and reference
material without any dependency on external services, cloud infrastructure,
or internet connectivity.

## Technology

| Concern | Choice |
|---|---|
| Language | Python |
| Framework | Django |
| UI | Server-rendered HTML |
| JavaScript | Minimal (strategy TBD) |
| Database | SQLite |
| Architecture | Monolithic |
| Authentication | Django built-in (server-side sessions) |
| External APIs | None |
| CDN | None |

## GTD Lists Supported

- Inbox (capture buffer)
- Next Actions (with context filtering)
- Projects (outcome-oriented, multi-action)
- Waiting For (delegated commitments)
- Agenda (by person and by meeting)
- Someday / Maybe (incubation)
- Reference (non-actionable material)
- Areas of Responsibility (organizational containers)

## Reviews

- Daily Review — fast orientation, transient focus selection
- Weekly Review — full system review, stuck-project detection

## Meeting Capture

- Recurring Meeting definitions
- Meeting Sessions (individual occurrences)
- Meeting Notes (rapid capture during a session, processed afterward)

## Project Status

Design approved. Documentation being established. Application implementation
has not started. See `docs/PROJECT_STATUS.md`.

## Documentation

| Document | Purpose |
|---|---|
| `docs/PRODUCT_REQUIREMENTS.md` | Product boundaries and GTD invariants |
| `docs/GTD_DOMAIN_MODEL.md` | Entities, relationships, lifecycles, date semantics |
| `docs/USER_WORKFLOWS.md` | All user-facing workflows |
| `docs/ARCHITECTURE.md` | Django structure and proposed pages |
| `docs/SECURITY.md` | Authentication and security model |
| `docs/AIR_GAP_DEPLOYMENT.md` | Offline deployment and packaging |
| `docs/ROADMAP.md` | Phased implementation plan |
| `docs/PROJECT_STATUS.md` | Current project state |
| `docs/DECISIONS_NEEDED.md` | Unresolved decisions |
| `docs/adr/` | Architecture Decision Records |
| `specs/` | Feature specifications |
| `CLAUDE.md` | Instructions for Claude sessions |

## Air-Gap Deployment

This application is designed to run without internet access. All dependencies
must be vendored before transfer to the target machine. See
`docs/AIR_GAP_DEPLOYMENT.md` for the full packaging and deployment procedure.

## Development

Development setup instructions will be added in Phase 1 of the roadmap.
