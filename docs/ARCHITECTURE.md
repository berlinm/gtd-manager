# Architecture

## 1. Technology Choices

| Concern | Choice | Rationale |
|---|---|---|
| Language | Python | See ADR 001 |
| Framework | Django | See ADR 001 |
| UI rendering | Server-side HTML | See ADR 003 |
| JavaScript | Minimal (strategy TBD) | See ADR 003 |
| Database | SQLite | See ADR 002 |
| Architecture | Monolithic | See ADR 001 |
| Auth | Django built-in | Single-user; no external IdP needed |
| External APIs | None | Air-gap requirement |
| CDN | None | Air-gap requirement |
| Node.js | Not required in production | Air-gap; server-rendered UI |

See `docs/adr/` for full rationale on each major decision.

---

## 2. Django Application Structure

```
gtd_manager/
├── config/
│   ├── settings/
│   │   ├── base.py       — shared settings
│   │   └── local.py      — dev overrides (not committed with secrets)
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── core/             — auth views, login/logout, common middleware,
│   │                       base templates, shared template tags and utilities
│   │                       NO domain entities
│   │
│   ├── gtd/              — all primary GTD domain entities and their views:
│   │                       Project, NextAction, WaitingFor, AgendaItem,
│   │                       SomedayMaybe, Reference, Person, Meeting,
│   │                       AreaOfResponsibility, Context, Tag
│   │
│   ├── capture/          — InboxItem, clarification workflow, inbox history
│   │
│   ├── meetings/         — MeetingSession, MeetingNote, meeting capture UI,
│   │                       note processing queue
│   │
│   ├── reviews/          — DailyReview, WeeklyReview, guided review workflows,
│   │                       stuck-project detection, review history
│   │
│   └── audit/            — audit event model, important-change logging,
│                           audit history views
│
├── templates/
│   ├── base.html
│   ├── partials/         — reusable HTML fragments
│   └── <app>/
│
├── static/
│   ├── css/
│   └── js/               — vendored libraries go here; no bundler required
│
├── manage.py
└── requirements.txt
```

### Inter-app dependency direction

```
core        ← (nothing; only Django itself)
gtd         ← core
capture     ← gtd, core
meetings    ← gtd, capture, core
reviews     ← gtd, capture, core
audit       ← any app it needs to observe
```

Apps import each other's models directly where needed. There is no requirement
to route ordinary foreign-key relationships through a generic intermediary layer.
Circular dependencies are avoided by design — `gtd` does not import from
`capture` or `meetings`.

---

## 3. Proposed Pages

| Page | URL Pattern | Purpose |
|---|---|---|
| Dashboard | `/` | Inbox count, stuck projects, today's scheduled actions, deadlines due soon, waiting-for follow-ups due |
| Daily Review | `/review/daily/` | Fast daily orientation; transient focus selection |
| Inbox (active) | `/inbox/` | Unprocessed items only |
| Clarify Item | `/inbox/<id>/clarify/` | Fast guided clarification |
| Inbox History | `/inbox/history/` | All processed items with dispositions |
| Next Actions | `/actions/` | Full list; filterable by context and area; grouped by availability |
| Today | `/actions/today/` | Overdue, scheduled-for-today, deadline-imminent |
| Projects | `/projects/` | Active projects with stuck flag; on-hold projects in separate section |
| Project Detail | `/projects/<id>/` | Outcome, actions grouped by availability, waiting-for, agenda items |
| Waiting For | `/waiting/` | All delegated commitments; sortable by `follow_up_on` and `expected_by` |
| Agenda | `/agenda/` | Sections: by person, by meeting |
| Someday / Maybe | `/someday/` | Incubation list |
| Reference | `/reference/` | Searchable reference library |
| Areas | `/areas/` | List and manage areas of responsibility |
| Meetings | `/meetings/` | List of recurring meetings |
| Meeting Detail | `/meetings/<id>/` | All sessions and associated agenda items |
| Meeting Session | `/meetings/<id>/sessions/<sid>/` | Notes for one session; processing queue |
| Weekly Review | `/review/weekly/` | Guided checklist |
| Review History | `/review/history/` | Past daily and weekly reviews |
| Settings | `/settings/` | Preferences, context/tag/person/meeting management |
| Login | `/login/` | The only unauthenticated page |

---

## 4. JavaScript Strategy

**Decision (2026-06-27):** Vendored htmx.

`htmx.min.js` is committed to `static/js/`. It enables partial-page updates
for the capture bar and clarification workflow without a build step or Node.js.
Templates use `partials/` for htmx target fragments. No other JavaScript
framework is used.

---

## 5. CSS Strategy

**Decision (2026-06-27):** Vendored classless CSS framework.

A single CSS file (e.g., Pico CSS) is committed to `static/css/`. It provides
sensible typographic defaults and form styling with minimal or no class
attributes required on most HTML elements. No build step required.

---

## 6. Production Server (TBD)

`django runserver` is a development-only server and must not be used in
production. The production WSGI server is TBD pending knowledge of the target
operating system and deployment topology.

Candidate options: gunicorn, uWSGI, mod_wsgi. The choice will be recorded in
a future ADR once the target environment is known.
