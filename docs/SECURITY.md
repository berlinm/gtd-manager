# Security Model

## 1. Authentication

Django's built-in authentication framework with server-side sessions. Sessions
are stored server-side using Django's session framework. The session backend
is TBD based on the deployment environment; Django's database-backed session
store is the default. The session cookie carries only a session key — user
data is not stored in the cookie itself.

All routes require login except `/login/`. Django's `LoginRequiredMixin` or
`@login_required` is applied consistently across all views.

Password reset via email is not available; there is no email infrastructure in
the air-gapped environment. Credential recovery is handled via
`manage.py changepassword` at the command line.

Password hashing uses Django's supported password-hashing framework. The
specific algorithm and work factor are determined by the Django version pinned
at implementation time. No algorithm is hardcoded in this document.

---

## 2. Session Configuration

| Setting | Value | Notes |
|---|---|---|
| `SESSION_COOKIE_HTTPONLY` | `True` | Django default |
| `SESSION_COOKIE_SAMESITE` | `'Strict'` | |
| `SESSION_COOKIE_SECURE` | TBD | Depends on HTTPS in the deployment environment |
| `ALLOWED_HOSTS` | TBD | Must be explicitly set to the deployment hostname or loopback address; never `'*'` |
| Session backend | TBD | Database-backed by default; confirmed when deployment topology is known |

---

## 3. CSRF

Django's CSRF middleware is enabled on all state-changing requests (POST, PUT,
PATCH, DELETE). No CSRF exemptions are granted without explicit documented
justification.

---

## 4. Content Security Policy

`Content-Security-Policy: default-src 'self'`

All assets (CSS, JavaScript, fonts, images) are served from the same origin.
No external sources are permitted. Since no CDN or third-party resources are
used, this header is unconditional.

**Open question:** The final treatment of any inline CSS and inline JavaScript
is not yet resolved. See `docs/DECISIONS_NEEDED.md` for the specific decision
about whether inline styles or scripts will require a `'unsafe-inline'`
directive or nonce-based exemption.

---

## 5. Additional Security Headers

| Header | Value |
|---|---|
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `same-origin` |

---

## 6. Application Data Security

- SQLite file is stored outside the web root; the path is configured via an
  environment variable
- `SECRET_KEY` is stored in an environment variable or a local `.env` file
  excluded from version control
- `DEBUG = False` in the deployed environment
- No user data is written to log files that could leave the machine

---

## 7. Authorization

This is a single-user MVP. Row-level authorization is not required.

No speculative `owner` foreign key is added to models for hypothetical
multi-user support. If multi-user support is introduced in the future, it will
require a separate design exercise.

---

## 8. HTTPS

Whether the application runs over HTTPS or plain HTTP is TBD and depends on
the deployment topology:

- If served only on `127.0.0.1`, plain HTTP may be acceptable
- If served on a local network hostname — even in an air-gapped environment —
  HTTPS with a self-signed certificate is strongly preferred
- `SESSION_COOKIE_SECURE` must be set accordingly

This decision is recorded in `docs/DECISIONS_NEEDED.md`.

---

## 9. Terminal Timestamp Naming Convention

**Open question:** Whether to name completion/cancellation timestamps
`completed_at`, `cancelled_at` (separate fields per terminal state), or
`closed_at` (a single field for all terminal transitions) has not been
resolved. See `docs/DECISIONS_NEEDED.md`.

The domain model in `docs/GTD_DOMAIN_MODEL.md` currently uses `completed_at`
as a placeholder. This will be updated once the convention is decided.
