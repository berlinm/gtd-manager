# Feature Specification: Phase 1 — Foundation and Inbox Capture

**Status:** Approved  
**Phase:** 1  
**Date:** 2026-06-27

---

## Goal

Establish the running Django project with authentication and a persistent,
frictionless inbox capture bar visible on every page. The inbox captures raw
thoughts with a title only; no categorization is required at capture time.

---

## User Story

> As the user, I want to type a thought into a capture bar on any page and
> submit it instantly, so that I never lose an idea while doing other work in
> the application.

---

## Functional Requirements

1. A login page accepts a username and password and establishes a server-side
   session. All other pages require authentication.
2. A logout action destroys the session and redirects to the login page.
3. A persistent capture bar is visible in the page header on every
   authenticated page.
4. The capture bar requires only a title (plain text). No other fields are
   shown during capture.
5. Submitting the capture bar creates an `InboxItem` with `disposition=pending`
   and `captured_at` set to the current time.
6. After submission the input clears and a brief "Captured." confirmation
   appears. The inbox count in the navigation updates without a full page reload.
7. An inbox page lists all unprocessed `InboxItem` records
   (`processed_at` is null) in reverse chronological order.
8. A dashboard page displays the current unprocessed inbox count with a link
   to the inbox.
9. Empty title submissions are silently ignored (no item created, no error).
10. The navigation links to: Dashboard, Inbox (with count).

---

## Acceptance Criteria

- [ ] Visiting any page while unauthenticated redirects to `/login/`
- [ ] Valid credentials create a session and redirect to the dashboard
- [ ] The capture bar is present in the header on the dashboard, inbox, and
      any other authenticated page
- [ ] Typing a title and pressing Enter (or clicking Capture) creates an
      InboxItem; the input clears and "Captured." appears
- [ ] The inbox count in the nav increments immediately after capture without
      a full page reload
- [ ] The inbox page shows all items with `processed_at` null
- [ ] Submitting an empty capture bar does nothing
- [ ] Logging out destroys the session and redirects to `/login/`
- [ ] No external URLs appear in any template, stylesheet, or script

---

## Non-Goals

- Clarifying or processing inbox items (Phase 2)
- Any GTD entity beyond `InboxItem`
- Pagination of the inbox list
- Editing or deleting inbox items
- Any mobile layout optimizations

---

## Domain Entities Affected

| Entity | Operation | Notes |
|---|---|---|
| `InboxItem` | Create, Read | `disposition` defaults to `pending`; `processed_at` null on creation |

---

## Validation Rules

| Rule | Where enforced |
|---|---|
| Empty title is rejected silently | View (POST handler) |
| Title is stripped of leading/trailing whitespace before save | View (POST handler) |

---

## Security Considerations

- All routes except `/login/` require authentication via `LoginRequiredMixin`
  or `@login_required`
- All POST requests are protected by Django's CSRF middleware
- The capture endpoint (`POST /inbox/capture/`) is login-required; an
  unauthenticated POST receives a redirect, not a 403
- No user-supplied data is rendered unescaped; Django templates auto-escape
  by default
- Static assets are served from `static/`; no external URLs in any template

---

## Air-Gap Considerations

- Pico CSS is vendored as `static/css/pico.min.css`
- htmx is vendored as `static/js/htmx.min.js`
- Both files are committed to the repository
- No `<link>` or `<script>` tag references an external hostname
- No new Python dependencies beyond Django are introduced in this phase

---

## Automated Tests

**Unit tests:**
- [ ] `InboxItem` with blank title is not created by the view
- [ ] `InboxItem.disposition` defaults to `pending` on creation
- [ ] `InboxItem.captured_at` is set automatically on creation
- [ ] `InboxItem.processed_at` is null on creation

**Integration tests (view/form):**
- [ ] GET `/login/` returns 200 for unauthenticated users
- [ ] GET `/` redirects unauthenticated users to `/login/`
- [ ] POST `/login/` with valid credentials creates a session and redirects to `/`
- [ ] POST `/inbox/capture/` with a title creates an InboxItem and returns the
      captured partial (200)
- [ ] POST `/inbox/capture/` with an empty title returns the captured partial
      but creates no InboxItem
- [ ] POST `/inbox/capture/` by an unauthenticated user redirects to login
- [ ] GET `/inbox/` returns 200 and lists unprocessed items
- [ ] GET `/inbox/` does not show items where `processed_at` is set

---

## Manual Acceptance Tests

**Golden path — capture and verify:**

1. Start the development server (`manage.py runserver`)
2. Navigate to `http://127.0.0.1:8000/`
3. Confirm redirect to `/login/`
4. Log in with the superuser credentials
5. Confirm redirect to the dashboard showing inbox count = 0
6. Type "Buy coffee" in the capture bar and press Enter
7. Confirm the input clears and "Captured." appears
8. Confirm the inbox count in the nav changes to 1 without a page reload
9. Click the Inbox link in the nav
10. Confirm "Buy coffee" appears in the list with a timestamp
11. Return to the dashboard; confirm count still shows 1

**Edge case — empty capture:**

1. Click in the capture bar without typing anything
2. Press Enter
3. Confirm nothing is created; no error is shown

**Edge case — session expiry:**

1. Log in
2. Delete the session cookie in the browser
3. Attempt to navigate to `/inbox/`
4. Confirm redirect to `/login/`
