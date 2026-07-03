# Decisions Needed

Unresolved decisions that must be made before or during specific implementation
phases. Do not silently resolve these — record the decision here when it is made.

---

## Blocking decisions (must resolve before Phase 1)

### CSS approach

**Options:**
- A: Hand-written CSS only — maximum control; no vendoring required
- B: Vendored classless CSS framework (e.g., Pico CSS) — single file; sensible
  defaults; minimal class usage
- C: Minimal utility-CSS build — requires a build step on a connected machine

**Impact:** Template structure throughout the project. Must be decided before
the first template is written.

**Status:** Resolved — see decision log (Pico CSS 2.0.6, vendored to `static/css/`)

---

### Minimal JavaScript strategy

**Options:**
- A: Plain form posts with full-page reloads — no JavaScript dependency; maximum
  simplicity
- B: Vendored htmx — single file (~15 KB) committed to `static/js/`; enables
  partial-page updates for the capture bar and clarification workflow; no build
  step required

**Impact:** Template and partial structure throughout Phases 1–6. Must be
decided before the first template is written.

**Status:** Resolved — see decision log (htmx 2.0.3, vendored to `static/js/`)

---

## Blocking decisions (must resolve before Phase 2)

### `scheduled_for` precision

**Options:**
- Date only — simpler; cannot represent "call at 2 PM"
- Datetime — can represent time-specific scheduled actions; affects Today view
  and form design

**Impact:** `NextAction` model field type; Today view display.

**Status:** Resolved — see decision log (DateTimeField)

---

### Reference body format

**Options:**
- Plain text — simplest
- Markdown with rendered output — richer display; adds a rendering dependency
  that must be vendored

**Impact:** `Reference` model; reference detail template.

**Status:** Resolved — see decision log (Markdown via mistune 3.0.2, vendored)

---

## Blocking decisions (must resolve before Phase 6)

### DailyReview focus list storage

**Options:**
- Django's session store — simplest; no additional model needed; cleared when
  session expires
- Short-lived model with expiry — explicit; queryable; requires a cleanup job
- Temporary database table cleared on daily review completion — explicit clear
  semantics

**Impact:** `reviews` app data model; daily review view logic.

**Constraint:** The chosen mechanism must ensure the focus list does not persist
beyond the daily review session or an explicit clear action. It must not alter
any item's GTD classification.

**Status:** Resolved — see decision log (Django session store)

---

### `last_activity_at` implementation strategy

**Options:**
- Computed on demand via a queryset annotation — simpler to maintain; may
  produce more complex queries
- Denormalized field on Project updated on child saves — faster to query;
  requires signal or save-override logic

**Impact:** `Project` model; project list and review queries.

**Status:** Resolved — see decision log (computed annotation)

---

## Blocking decisions (must resolve before Phase 7)

### Final CSP treatment of inline CSS and JavaScript

**Question:** Will any inline styles or scripts be present that require a
`'unsafe-inline'` directive or a nonce-based exemption to the
`Content-Security-Policy` header?

The target header is `Content-Security-Policy: default-src 'self'`. If any
templates or third-party vendored files emit inline styles or scripts, the
header must be adjusted.

**Impact:** `SECURITY_MIDDLEWARE` configuration; template review.

**Status:** Resolved — see decision log (no CSP header; inline scripts and styles retained; disproportionate for single-user localhost deployment)

---

### Backup invocation method

**Options:**
- Manual — run `manage.py backupdb` by hand when needed
- OS-level cron — scheduled automatically on the target machine
- In-application trigger — a settings page button or scheduled Django task

**Impact:** Operational documentation; Phase 7 deliverable.

**Status:** Resolved — see decision log (in-application trigger: Settings page "Backup now" button)

---

## Deployment decisions (must resolve before production)

### Deployment topology

What needs to be known:
- System service manager (e.g., systemd, supervisor, other)
- Whether a reverse proxy (e.g., nginx) sits in front of the WSGI server
- Network binding (`127.0.0.1` vs. a LAN interface)

**Impact:** `ALLOWED_HOSTS`; WSGI server choice; security headers.

**Status:** Resolved — see decision log (Windows 10 PC workstation; localhost only; no reverse proxy; Windows Task Scheduler or NSSM for service management)

---

### Production WSGI server

**Options:** gunicorn, uWSGI, mod_wsgi (others possible depending on OS)

`django runserver` is excluded — it is development-only.

**Impact:** Wheelhouse contents; deployment procedure documentation.

**Status:** Resolved — see decision log (waitress; gunicorn and uWSGI do not support Windows)

---

### HTTPS vs plain HTTP

**Options:**
- Plain HTTP on `127.0.0.1` loopback — acceptable if the application is only
  accessible from the local machine
- HTTPS with a self-signed certificate — required if the application is
  accessible from other machines on the local network, even in an air-gapped
  environment

**Impact:** `SESSION_COOKIE_SECURE`; certificate management.

**Status:** Resolved — see decision log (plain HTTP on 127.0.0.1; single-machine access only; SESSION_COOKIE_SECURE remains False)

---

### Session store backend

Django's database-backed session store is the default and is appropriate for
a single-user application. If the deployment topology introduces a reason to
prefer a different backend, this decision should be revisited.

**Status:** Resolved — see decision log (database-backed; confirmed for Windows 10 single-user deployment)

---

## Deferred design decisions

### Django version

**Impact:** Password-hashing algorithm defaults; LTS support window; any ORM
features used. Must be resolved before wheelhouse generation begins.

**Status:** Resolved — see decision log (Django 5.2)

---

### Existing data import

**Question:** Does the user have an existing GTD system (paper, another
application) that requires a migration path?

**Impact:** Potentially Phase 1 scope if a bare CSV-to-inbox import is needed
before the application is usable.

**Status:** TBD

---

## Non-blocking follow-up items

These are open questions that do not block any specific phase but should be
resolved before the affected code is finalized.

### Terminal timestamp naming convention

**Question:** How should timestamps for terminal state transitions be named?

- `completed_at` — a single field covering all terminal states
- Separate fields: `completed_at` / `cancelled_at` — one field per terminal
  status
- `closed_at` — a neutral term covering all terminal states

The domain model currently uses `completed_at` as a placeholder. The convention
must be consistent across all entities (Project, NextAction, WaitingFor).

**Status:** Unresolved

---

### Sidebar navigation icons

**Question:** Should the left sidebar nav items carry icons alongside their text labels?

- **Option A: No icons** — text-only, cleanest, no symbol set to choose or vendor
- **Option B: Unicode symbols** — zero dependencies; works inline; limited expressiveness
- **Option C: Vendored SVG sprite** — full control; requires choosing and committing an icon set; slight maintenance overhead

If icons are added, they must appear with visible labels (never icon-only), per `docs/UI_REFACTOR_PRINCIPLES.md` §3. Items with unambiguous icons: Inbox, Projects, Waiting For, Today, Reviews. Items harder to icon clearly: Someday/Maybe, Reference, Agendas.

**Status:** Deferred — hold until layout and capture placement are stable

---

## Decision log

| Decision | Resolved | Value | Notes |
|---|---|---|---|
| CSS approach | 2026-06-27 | Vendored classless CSS | Pico CSS 2.0.6; `static/css/pico.min.css`; committed to repo |
| JavaScript strategy | 2026-06-27 | Vendored htmx | htmx 2.0.3; `static/js/htmx.min.js`; committed to repo; no build step |
| `scheduled_for` precision | 2026-06-27 | DateTimeField | Supports time-specific actions; timezone handling in views |
| Reference body format | 2026-06-27 | Markdown with rendering | mistune 3.0.2 vendored; `gtd_tags.markdown` template filter |
| `last_activity_at` strategy | 2026-06-27 | Computed annotation | `Greatest(Max(...))` queryset annotation on demand; no stored field |
| Django version | 2026-06-27 | Django 5.2 | LTS release; in use since Phase 1 |
| DailyReview focus list storage | 2026-06-27 | Django session store | `request.session['gtd_focus_pks']` list of PKs; cleared explicitly or on session expiry; no GTD classification altered |
| Backup invocation | 2026-06-27 | In-application trigger | Settings page "Backup now" button; `manage.py backupdb` also available |
| Deployment topology | 2026-06-27 | Windows 10 PC workstation | Localhost only; 127.0.0.1; no reverse proxy; NSSM or Task Scheduler for service |
| Production WSGI server | 2026-06-27 | waitress | Pure-Python; Windows-compatible; gunicorn/uWSGI excluded (no Windows support) |
| HTTPS vs plain HTTP | 2026-06-27 | Plain HTTP on 127.0.0.1 | Single-machine only; SESSION_COOKIE_SECURE = False |
| Session store backend | 2026-06-27 | Database-backed (default) | Appropriate for single-user; no topology reason to change |
| CSP treatment | 2026-06-27 | No CSP header | Inline scripts/styles retained; strict CSP disproportionate for single-user localhost app |
| CSS approach (revised) | 2026-07-03 | Bespoke design system | Pico CSS removed; single hand-written `static/css/app.css` with design tokens, light/dark themes, component classes; governed by `docs/UI_REFACTOR_PRINCIPLES.md` |
