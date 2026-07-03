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
| Phase 5 — Meeting Capture | Complete |
| Phase 6 — Reviews | Complete |
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

**Meetings**
- Meeting records (recurring targets): create, edit, list, detail
- MeetingSession: start session for a meeting; date, optional start/end times
- Live session capture: htmx rapid-note entry (title only, no friction)
- Agenda items for the meeting shown alongside the capture bar during a session
- Close session: sets `closed_at`; unprocessed notes enter processing queue
- Post-session note clarify: all same dispositions as inbox clarify
- Processed notes retained on session page with disposition shown
- Meetings nav link with pending-notes badge (unprocessed from closed sessions)
- Redirects to project detail when note processed as new project; to session otherwise

**Reviews**
- Daily review: inbox status, scheduled today, deadlines (7-day horizon), follow-ups due, stuck projects, focus selection
- Focus list stored in Django session; displayed in nav with count; cleared explicitly or on new daily review without focus
- Weekly review: all 9 GTD steps with live data (inbox, projects, on-hold, deadlines, waiting-for, someday/maybe, agenda, upcoming)
- Review history page showing last 20 daily and weekly reviews
- Review nav link (highlights when in reviews app; shows focus count badge when focus is active)

**Cross-cutting**
- Bespoke design system (`static/css/app.css`, no CSS framework): design tokens, light/dark themes, sidebar shell with GTD-grouped nav and live count badges, sticky capture bar with `/` keyboard shortcut and inline "✓ Captured" feedback
- Clarify screens use progressive disclosure: actionable dispositions are tabs revealing one panel at a time
- Responsive below ~880 px (off-canvas sidebar with hamburger toggle); `prefers-reduced-motion` respected
- Dark / light mode (localStorage)
- Login / logout; all views require authentication
- 162 automated tests (model validation + view/workflow integration)
- Manual test plan in `docs/MANUAL_TEST_PLAN.md` (22 sections)

## Next intended work

**Phase 7 — Hardening**

- `audit` app: audit event model; logging of important changes
- CSP and all security headers configured
- Full offline asset audit
- `manage.py backupdb` management command
- Validated restore procedure
- Wheelhouse build and transfer documentation
- Pre-deployment checklist verified

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
| Phase 5 | 2026-06-26 | Meeting capture, session notes, note clarify, pending badge |
| Phase 6 | 2026-06-27 | Daily review, weekly review, focus list (session), review history |
| UI redesign | 2026-07-03 | Pico CSS replaced with bespoke design system; sidebar shell, capture bar signature element, clarify progressive disclosure, light/dark themes |
