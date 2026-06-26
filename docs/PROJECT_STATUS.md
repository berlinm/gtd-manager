# Project Status

## Current state

| Item | Status |
|---|---|
| Design | Approved (Revision 3) |
| Project documentation | Complete |
| Phase 1 — Foundation | Complete |
| Phase 2 — Clarification and Next Actions | Complete |
| Phase 3 — Delegation, Agenda, Incubation | Complete |
| Phase 4 — Reference, Areas, Inbox History | Complete |
| Phase 5 — Meeting Capture | Not started |
| Phase 6 — Reviews | Not started |
| Phase 7 — Hardening | Not started |

## What is working

**Capture**
- Persistent capture bar on all pages; htmx inline confirmation
- Inbox list with process/clarify workflow
- All seven dispositions: trash, done immediately, someday/maybe, reference,
  delegate, single next action, new project, add action to existing project
- Inbox history (processed items with dispositions and links to created objects)

**Next Actions**
- Full model with three date fields (`defer_until`, `scheduled_for`, `deadline`)
- Chronological validation enforced
- List filtered to available (non-deferred) actions; context filter
- Today view: scheduled-for-today, deadlines
- Done / cancel / delegate actions from the list

**Projects**
- Project list with stuck-project detection and on-hold section
- Project detail: actions grouped by available / deferred / scheduled
- Waiting-for items and received delegations visible on project detail
- Agenda items visible on project detail

**Waiting For**
- Full model with all date fields
- List with follow-up highlighting; follow-up date update workflow
- Receive workflow: saves result notes; redirects to linked project if set
- Cancel workflow
- Delegate-from-action shortcut (cancels action, creates waiting-for)
- History page (`/waiting/history/`) with result notes
- Optional project assignment on creation and from clarify delegate flow

**Agenda**
- AgendaItem with person XOR meeting constraint enforced
- Agenda view grouped by person and by meeting
- Mark raised (delete)

**Someday / Maybe**
- List; promote-to-project workflow

**Reference**
- Full-text search (title + body)
- Markdown body rendered as HTML
- Tags and area assignment

**Areas of Responsibility**
- Area list and edit
- Area detail: active projects, on-hold projects, standalone actions, reference,
  someday items

**Dashboard**
- Inbox count, waiting-for follow-ups due, stuck project count

**Cross-cutting**
- Dark / light mode (localStorage)
- Login / logout; all views require authentication
- 99 automated tests (model validation + view/workflow integration)
- Manual test plan in `docs/MANUAL_TEST_PLAN.md` (19 sections)

## Next intended work

**Phase 5 — Meeting Capture**

- `meetings` app: `MeetingSession`, `MeetingNote` models
- Meeting session capture UI; rapid-note entry during a session
- Post-meeting note processing queue (same clarification flow as inbox)
- Meeting detail page with session history
- Agenda items for a meeting visible during an active session

See `docs/ROADMAP.md` for full phase definitions.

## Unresolved decisions

See `docs/DECISIONS_NEEDED.md`. No decisions have been silently resolved.

## Revision history

| Revision | Date | Summary |
|---|---|---|
| Revision 1 | 2026-06-27 | Initial design proposal |
| Revision 2 | 2026-06-27 | Corrections to entities, date semantics, app structure |
| Revision 3 | 2026-06-27 | Final corrections; approved as baseline |
| Documentation | 2026-06-27 | Permanent project documentation established |
| Phases 1–3 | 2026-06-27 | Foundation, clarification, delegation, agenda, incubation |
| Phase 4 | 2026-06-27 | Reference, area detail, inbox history |
| Clarify + WaitingFor | 2026-06-27 | Bug fixes, project integration, delegation history |
