---
description: Verify a GTD Manager change by running the real app in a browser and observing behavior, not just reading the diff. Use when asked to verify a fix, confirm a bug is resolved, or check a UI/workflow change before reporting it done.
---

This is a server-rendered Django app with minimal JS — most "does it work" questions
are answered by loading a page and looking, not by reading templates.

1. Start the dev server in the background:
   `.venv\Scripts\python.exe manage.py runserver 8000`
   (settings module is `config.settings.local`; `DEBUG=True`, `ALLOWED_HOSTS` includes
   `127.0.0.1`/`localhost`. Do not change these for verification.)
2. Do not create a new superuser or fixture data. `db.sqlite3` already holds the
   single user's real data — log in with the existing account. If credentials are
   needed and unknown, ask rather than resetting the password or creating a user.
3. Use the claude-in-chrome tools to open `http://127.0.0.1:8000/`, log in, and
   navigate to the specific page under test. Screenshot before/after when checking
   a visual bug fix.
4. Check `docs/MANUAL_TEST_PLAN.md` for the numbered section covering the feature —
   it documents expected behavior per workflow and is the closest thing this project
   has to an acceptance spec. If the change adds a new workflow, a test plan section
   should already have been added in the same commit (see CLAUDE.md); flag it if not.
5. Exercise the golden path plus the specific edge case the bug/fix was about — e.g.
   for a CSS layout fix, also check the opposite theme (light/dark) and a narrow
   viewport (<880px, where the sidebar goes off-canvas per the test plan).
6. Report what you actually observed (with a screenshot), not just that the code
   looks correct. If you can't run the browser step, say so explicitly instead of
   claiming verification happened.
7. Stop the dev server when done.
