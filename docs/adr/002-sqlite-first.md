# ADR 002 — SQLite as the Primary Database

**Status:** Accepted  
**Date:** 2026-06-27

---

## Context

The application is single-user, self-hosted, and air-gapped. It does not
require concurrent write access from multiple processes or users. The data
volume is that of a personal productivity system: thousands to tens of
thousands of rows across a moderate number of tables.

Deploying and maintaining a separate database server (PostgreSQL, MySQL) in an
air-gapped single-user environment adds significant operational complexity for
no benefit in this use case.

---

## Decision

Use **SQLite** as the primary database.

Django supports SQLite natively. The database is a single file stored on the
local filesystem, outside the web root, with its path configured via an
environment variable.

SQLite's write serialization is not a constraint for a single-user application.
Django's ORM abstracts the database engine; migrating to PostgreSQL in the
future, if ever required, is mechanical.

---

## Consequences

**Positive:**
- No separate database server process to install, configure, or maintain
- Database is a single file — easy to back up, inspect, and transfer
- Zero additional dependencies beyond Python's standard library `sqlite3`
- Django's ORM provides all required query capabilities
- SQLite's WAL mode (if enabled) provides good read concurrency for the
  rare case of simultaneous reads during a browser session

**Negative / accepted tradeoffs:**
- Write operations are serialized — not a constraint for single-user use
- Full-text search requires SQLite FTS (available as a Django add-on or via
  raw SQL); less capable than PostgreSQL's full-text search — acceptable for
  the reference library search use case in the MVP
- Some advanced PostgreSQL features (e.g., `JSONB` indexing, advisory locks)
  are unavailable — none are required by this application

**Backup requirement:**
Copying a live SQLite file during writes is unsafe. The backup mechanism must
use the SQLite Backup API (via `sqlite3.Connection.backup()`) or a controlled
application stop. See `docs/AIR_GAP_DEPLOYMENT.md`.

**Migration path:**
If PostgreSQL or another server-based database is ever required (e.g., for
multi-user support), Django's ORM makes the migration mechanical: update
`DATABASES` in settings, run `manage.py migrate`, and import data. No
application code changes are required if SQLite-specific features have been
avoided.
