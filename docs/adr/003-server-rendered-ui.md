# ADR 003 — Server-Rendered HTML with Minimal JavaScript

**Status:** Accepted  
**Date:** 2026-06-27

---

## Context

The application runs in an air-gapped environment. The UI must function without
internet access and without a JavaScript build pipeline at deployment time.

The primary user is working at a desktop computer. The interaction model is
list-heavy with forms for data entry. It does not require real-time
collaboration, streaming data, or complex client-side state management.

The following UI technology directions were considered:

- Full server-rendered HTML with no JavaScript
- Server-rendered HTML with vendored htmx for partial updates
- Server-rendered HTML with a lightweight JavaScript framework (Alpine.js, etc.)
- A decoupled React or Vue frontend with a Django REST API backend

---

## Decision

Use **server-rendered HTML** (Django templates) as the primary UI layer, with
**minimal JavaScript** whose specific strategy is TBD.

Two options remain under active consideration for the JavaScript layer:

**Option A — Plain form posts with full-page reloads**
- No JavaScript dependency at all
- Maximum simplicity; no vendoring of JS files required
- Some workflows (the persistent capture bar, the clarification page) involve
  visible page reloads

**Option B — Vendored htmx**
- A single file (~15 KB) committed to `static/js/`
- Enables partial-page updates for the capture bar and clarification workflow
  without a build step
- No additional JavaScript framework; no Node.js required
- Compatible with air-gap deployment: the file is committed to the repo

The choice between Option A and Option B is recorded in
`docs/DECISIONS_NEEDED.md` and must be made before Phase 1 templates are
written.

In either case, the following is true and accepted:

- No React, Vue, Angular, or other JavaScript component framework
- No JavaScript build pipeline (webpack, Vite, etc.) required in production
- No Node.js required in production
- All JavaScript, if any, is vendored as plain files in `static/js/`

---

## Consequences

**Positive:**
- Django templates are a well-understood, maintainable approach for a solo
  developer
- No build pipeline in production simplifies air-gap deployment significantly
- All UI state is authoritative on the server; no client-server state
  synchronization problems
- Full-page reloads are acceptable for a desktop-first, single-user application
  where interaction density is moderate

**Negative / accepted tradeoffs:**
- Without htmx, some interactions (rapid note capture during a meeting, the
  capture bar) will cause full-page reloads — acceptable but less fluid
- A decoupled API cannot be added incrementally later without a significant
  architectural change — accepted because no API is planned

**Desktop-first:**
The application is designed for desktop use. Mobile layout optimization is
explicitly out of scope for the MVP.
