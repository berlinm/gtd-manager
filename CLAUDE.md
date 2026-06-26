# CLAUDE.md

This file contains permanent instructions for Claude sessions working on this project.

## Project identity

A single-user, air-gapped GTD (Getting Things Done) web application.
Stack: Python, Django, server-rendered HTML, SQLite, minimal JavaScript.
No Node.js, no external APIs, no cloud services, no CDN dependencies.

## Design baseline

Revision 3 of the design proposal is the approved baseline. Read it before
making architectural or domain decisions:

- `docs/PRODUCT_REQUIREMENTS.md` — product boundaries and GTD invariants
- `docs/GTD_DOMAIN_MODEL.md` — entities, relationships, status lifecycles, date semantics, validation rules
- `docs/USER_WORKFLOWS.md` — all user-facing workflows
- `docs/ARCHITECTURE.md` — Django app structure and proposed pages
- `docs/SECURITY.md` — authentication, session, and content security
- `docs/AIR_GAP_DEPLOYMENT.md` — offline dependency packaging and deployment constraints
- `docs/ROADMAP.md` — phased implementation plan and deferred capabilities
- `docs/DECISIONS_NEEDED.md` — unresolved decisions; do not silently resolve them

## GTD domain rules (non-negotiable)

These distinctions must be preserved in every implementation decision:

1. **InboxItem** — raw capture only; disappears from the active view after clarification but is retained with a disposition record.
2. **NextAction** — a concrete physical action; never carries a `delegated_to` field; never has a `delegated` status.
3. **Project** — an outcome requiring more than one action; has its own optional `deadline` separate from any action deadline; stuck state is derived, not stored.
4. **WaitingFor** — first-class delegated commitment; structurally separate from NextAction; carries `expected_by` (delivery date) and `follow_up_on` (check-in date) as distinct fields.
5. **AgendaItem** — not a next action; no date fields; belongs to exactly one Person XOR one Meeting.
6. **SomedayMaybe** — not an active commitment; invisible to action lists and stuck-project detection.
7. **Reference** — no action fields (no deadline, no status, no scheduled dates).
8. **Meeting** — a recurring agenda target (entity); not a one-time occurrence.
9. **MeetingSession** — one occurrence of a Meeting; contains MeetingNotes.
10. **MeetingNote** — raw capture during a session; processed after the meeting like an InboxItem.
11. **DailyReview** — fast daily orientation; the focus list it produces is transient and must not alter any item's GTD classification.
12. **WeeklyReview** — the primary review; surfaces stuck projects, empty inbox requirement, upcoming deadlines.

## Date semantics (three separate fields on NextAction)

- `defer_until` — action unavailable before this date
- `scheduled_for` — action must occur on this specific date/time
- `deadline` — must be completed no later than this date (real external commitment only)

These are never merged into a single field. Chronological validation rules apply; see `docs/GTD_DOMAIN_MODEL.md`.

WaitingFor has separate date fields: `delegated_at`, `expected_by`, `follow_up_on`, `last_follow_up_at`.

## Django application structure

```
apps/core/      — auth views, middleware, base templates, shared utilities (no domain entities)
apps/gtd/       — all primary GTD entities and their views
apps/capture/   — InboxItem, clarification workflow
apps/meetings/  — MeetingSession, MeetingNote
apps/reviews/   — DailyReview, WeeklyReview
apps/audit/     — audit event logging
```

Apps import each other's models directly; no generic intermediary layer required.
Dependency direction: capture → gtd; meetings → gtd, capture; reviews → gtd, capture; audit → any.
`core` does not import domain entities.

## Air-gap constraints

- All static assets (CSS, JS, fonts) must be vendored into `static/`. No external URLs in any template.
- Python dependencies are distributed as a wheelhouse built on a matching OS/architecture/Python version.
- `django runserver` is development-only; the production WSGI server is TBD.
- No runtime calls to any external host.

## What is TBD

Do not silently resolve these; see `docs/DECISIONS_NEEDED.md`:
- Deployment topology and WSGI server
- HTTPS vs plain HTTP
- Session store backend
- `scheduled_for` precision (date vs datetime)
- Reference body format
- `last_activity_at` implementation strategy
- DailyReview focus list storage
- Backup invocation method
- Django version
- Existing data import path

## Living documentation

Keep these files current as implementation progresses. Update them in the **same commit** as the code they describe — never defer documentation.

### Every feature or workflow added
- **`docs/MANUAL_TEST_PLAN.md`** — add a numbered section covering the happy path and key edge cases. No feature ships without a test plan section. This is a standing requirement.

### Every phase completed, or significant capability added
- **`docs/PROJECT_STATUS.md`** — update the phase status table, the "What is working" inventory, and "Next intended work". Reflect the actual running app, not the roadmap plan.

### Every implementation decision (technology choice, field type, library, pattern)
- **`docs/DECISIONS_NEEDED.md`** — mark the item's `Status:` line as `Resolved — see decision log` and append a row to the Decision Log table at the bottom with the date and value chosen. Never implement a decision without recording it. The log is the audit trail.

### When actual code structure diverges from the docs
- **`docs/ARCHITECTURE.md`** — update the technology table (section 1), app list (section 2), or page inventory (section 3) if the real code differs. The table row "JavaScript | Minimal (strategy TBD)" should have been updated when htmx was adopted.

### Domain model changes (rare)
- **`docs/GTD_DOMAIN_MODEL.md`** — update only when an entity, field, or validation rule genuinely changes. Treat this as the authoritative source; change it deliberately and update the GTD domain rules section of this file if affected.

### Documents that must NOT be routinely edited
- `docs/PRODUCT_REQUIREMENTS.md` — stable scope definition; change only if requirements change.
- `docs/USER_WORKFLOWS.md` — stable workflow descriptions; change only if a workflow changes.
- `docs/SECURITY.md` / `docs/AIR_GAP_DEPLOYMENT.md` — change only if security or deployment approach changes.
- `docs/adr/*.md` — ADRs are immutable once written; write a new ADR rather than amending an existing one.
- `docs/ROADMAP.md` — the phased plan; do not mark phases complete here; use `docs/PROJECT_STATUS.md` for current state.

## Code conventions

- No comments unless the WHY is non-obvious.
- No speculative features or abstractions beyond what the current phase requires.
- No owner FK added for hypothetical multi-user support.
- No external dependencies introduced without updating the wheelhouse documentation.
- `DEBUG = False` in production settings.
- `ALLOWED_HOSTS` must be explicitly set; never `'*'`.
