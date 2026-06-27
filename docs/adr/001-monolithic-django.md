# ADR 001 — Monolithic Django Application

**Status:** Accepted  
**Date:** 2026-06-27

---

## Context

This is a single-user personal productivity application deployed in an
air-gapped environment. It requires:

- No external APIs or cloud services
- No multi-user features in the MVP
- Deployment on a single machine with no network access
- Minimal operational complexity for a solo user

The technology choice must support server-rendered HTML, local SQLite storage,
and an offline-first deployment model without requiring a JavaScript build
pipeline or Node.js in production.

Several architecture patterns were considered:
- Monolithic Django application
- Django with a decoupled JavaScript frontend (React, Vue, etc.)
- Microservices
- A non-Django Python web framework

---

## Decision

Use a **monolithic Django application** with server-rendered HTML and minimal
JavaScript.

Python was chosen as the implementation language. Django provides:

- A mature ORM well-suited to SQLite
- Built-in authentication and session management
- A robust form validation framework that maps naturally to the GTD domain's
  validation rules
- A template system that supports server-rendered HTML without a build step
- A large ecosystem of vendorable packages
- A management command framework suitable for backup and maintenance operations

The application is structured as a single deployable unit with multiple
Django apps organized by functional domain (`core`, `gtd`, `capture`,
`meetings`, `reviews`, `audit`).

---

## Consequences

**Positive:**
- Single process to deploy, monitor, and restart
- No JavaScript build pipeline required in production
- All static assets can be vendored as plain files
- Django's ORM handles SQLite transparently
- Django's built-in authentication satisfies the single-user requirement
  without additional dependencies
- Easier to reason about for a solo developer and maintainer

**Negative / accepted tradeoffs:**
- Some UI interactions (capture bar, partial updates) may feel slower with
  full-page reloads if the plain-forms option is chosen over htmx
- If multi-user support is ever added, a more significant refactor is required
  than if a decoupled API had been built from the start — accepted because
  multi-user support is not a goal

**Out of scope by this decision:**
- React, Vue, Angular, or any other JavaScript frontend framework
- Separate API server or microservices
- Redis, Celery, or any asynchronous task queue
- Any cloud service dependency
- Node.js in production
