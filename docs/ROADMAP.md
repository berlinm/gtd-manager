# Implementation Roadmap

## Phase 1 — Foundation

**Goal:** A running Django project with authentication and bare inbox capture.

- Django project skeleton with settings split (`base.py`, `local.py`)
- `core` app: authentication views (login / logout), base template, navigation
  shell
- `gtd` app: `AreaOfResponsibility`, `Context`, `Person`, `Meeting`, `Tag`
  models (no views yet beyond admin)
- `capture` app: `InboxItem` model, persistent capture bar on all pages,
  active inbox list
- Dashboard stub (inbox count only)
- Confirm no external URLs in any template

---

## Phase 2 — Clarification and Next Actions

**Goal:** Inbox items can be clarified. Projects and next actions are usable.

- Clarification workflow in `capture`; `disposition` and generic FK recorded
  on `InboxItem`
- `gtd` app: `NextAction` model (all three date fields: `defer_until`,
  `scheduled_for`, `deadline`), `Project` model (all fields including
  `deadline`, `last_reviewed_at`, `next_review_on`)
- Chronological validation rules on `NextAction` enforced in `clean()`
- All validation rules from `docs/GTD_DOMAIN_MODEL.md` enforced
- Next-actions list with context filter; grouped by availability (available
  now / deferred / scheduled)
- Project list (stuck-project flag visible); on-hold projects in separate
  section
- Project detail view (actions grouped by available / deferred / scheduled)
- Today view (scheduled-for-today + overdue + imminent deadlines)

---

## Phase 3 — Delegation, Agenda, and Incubation

**Goal:** WaitingFor, AgendaItem, and SomedayMaybe are fully usable.

- `WaitingFor` model (all date fields: `delegated_at`, `expected_by`,
  `follow_up_on`, `last_follow_up_at`, `result_notes`) and list page
- `AgendaItem` model with XOR validation (person XOR meeting); agenda view
  grouped by person and by meeting
- `SomedayMaybe` model and list; promotion-to-project workflow
- Project detail updated to show associated waiting-for items and agenda items
- Dashboard updated: follow-ups due today, stuck projects
- Delegation workflow (cancel NextAction → create WaitingFor)

---

## Phase 4 — Reference, Areas, and Inbox History

**Goal:** Reference material is usable; area views exist; processed inbox is
visible.

- `Reference` model, list, and search
- Area of responsibility detail view (associated projects, actions, reference)
- Inbox history view (processed items with dispositions and links to created
  objects)
- SomedayMaybe promotion history visible

---

## Phase 5 — Meeting Capture

**Goal:** Meetings can be captured and notes processed.

- `meetings` app: `MeetingSession`, `MeetingNote` models
- Meeting session capture UI; rapid-note entry (title only during session)
- Post-meeting note processing queue (same clarification flow as inbox)
- Meeting detail page; session history
- Agenda items for a meeting visible during an active session

---

## Phase 6 — Reviews

**Goal:** Daily and weekly review workflows are complete.

- `reviews` app: `DailyReview`, `WeeklyReview` models
- Guided daily review workflow: urgent inbox, scheduled today, deadlines,
  waiting-for follow-ups, focus selection, stuck projects
- Transient focus list mechanism (storage strategy TBD; see
  `docs/DECISIONS_NEEDED.md`)
- Guided weekly review checklist (all steps from `docs/USER_WORKFLOWS.md`)
- Stuck-project detection logic
- Review history page

---

## Phase 7 — Hardening

**Goal:** The system is production-ready and deployable in the air-gapped
environment.

- `audit` app: audit event model; logging of important changes
- CSP and all security headers configured (resolve inline CSS/JS decision first;
  see `docs/DECISIONS_NEEDED.md`)
- Full offline asset audit: confirm no external URLs in any template or
  stylesheet
- `manage.py backupdb` management command (SQLite Backup API)
- Validated restore procedure
- Wheelhouse build and transfer documentation
- Pre-deployment checklist (from `docs/AIR_GAP_DEPLOYMENT.md`) verified
- Credential recovery runbook
- `django runserver` confirmed absent from all production configuration

---

## Capabilities Deferred to Later Phases

The following capabilities are acknowledged as valuable. They will be addressed
after the core GTD workflows are stable. No phase assignment has been made yet.

| Capability | Notes |
|---|---|
| Global search | Full-text search across all entity types |
| Full backup and validated restore | `manage.py backupdb` is Phase 7; validated restore is a separate deliverable |
| JSON export | Complete data export in a machine-readable format |
| CSV export | Projects, next actions, and waiting-for items in tabular form |
| Human-readable GTD export | A printable or plain-text representation of the full active system for offline review |
| Audit logging for important changes | `audit` app scaffolded in Phase 7; comprehensive coverage is deferred |
| Daily review | Phase 6 |
| Meeting capture | Phase 5 |
| On-hold project review reminders | `next_review_on` field exists in Phase 2; surfacing it in daily/weekly review is a Phase 6 detail |
