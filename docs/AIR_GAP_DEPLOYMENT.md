# Air-Gap Deployment

This application is designed to run in an environment with no internet
connectivity. All external dependencies must be resolved and vendored before
transfer to the target machine.

---

## 1. Static Assets

All CSS, JavaScript, and fonts must be vendored into `static/`. No template,
stylesheet, or script may reference an external hostname in a `<link>`,
`<script>`, `<img>`, `<source>`, or CSS `@import`.

**System fonts are preferred** to avoid font-file vendoring complexity.

If a CSS framework, icon set, or htmx is adopted, those files must be
committed to the repository in `static/` before deployment.

A pre-deployment audit must confirm that no external URLs exist in any
template or stylesheet. This audit is a Phase 7 deliverable.

---

## 2. Python Dependencies

### Packaging mechanism: wheelhouse

The standard mechanism for offline Python dependency installation is a
**wheelhouse**: a directory of pre-built `.whl` files.

**Generating a wheelhouse (on a connected machine):**

```
pip download -d wheelhouse/ -r requirements.txt
```

**Installing from a wheelhouse (on the air-gapped machine):**

```
pip install --no-index --find-links=wheelhouse/ -r requirements.txt
```

### Critical constraint: environment matching

The wheelhouse **must be generated on a machine that exactly matches the
production environment**:

- Same operating system (e.g., Ubuntu 22.04, not macOS or Windows)
- Same CPU architecture (e.g., x86_64, not arm64)
- Same Python version (e.g., Python 3.11.x, not 3.12.x)

A wheelhouse built on a different OS or architecture will contain incompatible
binary wheels (e.g., compiled C extensions such as those in cryptographic
libraries) and must not be used as the deployment artifact.

If the development machine differs from the production machine, a matching
build environment must be set up (e.g., a virtual machine or container) solely
for wheelhouse generation.

### Requirements pinning

`requirements.txt` must pin exact versions for all direct and transitive
dependencies. Use `pip freeze` or a tool such as `pip-compile` to generate a
fully pinned file.

Do not use version ranges (e.g., `Django>=4.2`) in the production requirements
file.

---

## 3. Production WSGI Server

`django runserver` is a development-only server and **must not be used in
production**.

The production WSGI server is **TBD** pending knowledge of the target operating
system and deployment topology. Candidate options include gunicorn, uWSGI, and
mod_wsgi.

The selected server must also be included in the wheelhouse.

---

## 4. Deployment Topology (TBD)

The following deployment details are not yet resolved:

- **Service management:** Whether the application runs as a systemd service,
  a supervised process, or another arrangement
- **Network binding:** Whether it binds to `127.0.0.1` (loopback only) or a
  local network interface
- **HTTPS:** Whether a self-signed certificate is used; whether a local reverse
  proxy (e.g., nginx) is in front of the WSGI server
- **`ALLOWED_HOSTS`:** Must be set to the specific hostname or IP address once
  topology is known

---

## 5. Django Settings for Production

The following settings must be confirmed for the production environment:

| Setting | Required value |
|---|---|
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | TBD — must be explicitly set |
| `SECRET_KEY` | Loaded from environment variable or `.env` file; never committed |
| `EMAIL_BACKEND` | `'django.core.mail.backends.dummy.EmailBackend'` |
| `SESSION_COOKIE_SECURE` | TBD — depends on HTTPS decision |
| `DATABASES['default']['NAME']` | Absolute path outside the web root |

No development middleware (`django-debug-toolbar`, etc.) in production settings.

---

## 6. Database Backup

Copying a live SQLite file while the application is writing to it is unsafe
and may produce a corrupt backup. The backup mechanism must use one of:

### Implemented: `manage.py backupdb` (SQLite Backup API + media)

`manage.py backupdb` (also the Settings → **Back up now** button) writes a single
timestamped archive `backups/gtd-<YYYY-MM-DD_HHMMSS>.zip` containing:

- `db.sqlite3` — a **consistent snapshot** taken with `sqlite3.Connection.backup()`
  on the live connection (safe while the app is running; not an ad-hoc file copy).
- `media/` — the entire media tree, i.e. all reference file attachments.

This means a single backup artifact captures the complete application state
(database **and** uploaded files) and is trivially portable to another machine.

- **Destination:** `BACKUP_DIR` (`backups/`, gitignored).
- **Invocation:** manual — `manage.py backupdb`, or the in-app Settings button.
- **Retention:** none automated; prune old `.zip`s by hand if needed.
- **Legacy:** older database-only `gtd-*.db` backups remain listed in Settings.

### Restore procedure

1. Stop the application (waitress / the runserver process).
2. Unzip the chosen `gtd-<timestamp>.zip`.
3. Copy `db.sqlite3` to the project root (replacing the existing database).
4. Copy the `media/` directory to the project root (replacing/merging `media/`).
5. Restart the application and verify: log in, open a reference with an
   attachment, confirm the file downloads.

A rehearsed restore on the target machine is still recommended before relying on
backups in production.

---

## 7. Security Patches and Upgrades

The application does not self-update. Applying security patches requires:

1. Download updated packages on a connected machine
2. Regenerate the wheelhouse with the updated packages on a matching build
   environment
3. Transfer the updated wheelhouse to the air-gapped machine
4. Reinstall with `pip install --no-index --find-links=wheelhouse/`
5. Run `manage.py migrate` if any database migrations are included
6. Restart the WSGI server

This procedure must be documented and tested before go-live.

---

## 8. Pre-Deployment Checklist

The following must be confirmed before each deployment:

- [ ] All templates contain no external URLs
- [ ] `requirements.txt` is fully pinned
- [ ] Wheelhouse was generated on a matching OS/arch/Python environment
- [ ] `DEBUG = False` in production settings
- [ ] `ALLOWED_HOSTS` explicitly set
- [ ] `SECRET_KEY` loaded from environment; not hardcoded
- [ ] SQLite file path is outside the web root
- [ ] Backup procedure documented and tested
- [ ] Restore procedure documented and tested
- [ ] `django runserver` not referenced in any production configuration
- [ ] No development middleware active in production settings
