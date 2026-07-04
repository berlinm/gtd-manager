---
description: Organize a working session's running context log into a verified end-of-session summary. Use at the end of a session, or when asked to wrap up / summarize / close out the session, to turn the running notes in docs/sessions/ into a structured, complete, git-cross-checked record.
---

Turn this session's running log into a clean, verified summary. Run before ending
the session. See the "Session logging" section of `CLAUDE.md` for the running-log
convention this depends on.

1. Locate this session's running log under `docs/sessions/` — the
   `<YYYY-MM-DD>-<slug>.md` file appended to during the session. If none exists
   (the running log was skipped), reconstruct one from the conversation and git
   history before continuing, and note that it was reconstructed.

2. Establish the ground truth of what actually happened — do NOT rely on memory:
   - `git log --oneline` for the session's commit range (since the session's first
     commit, or since the last session log's HEAD).
   - `git diff --stat` over that range for files touched.
   - Which tests were run and their result; migrations applied; what was pushed,
     merged, or deployed (and to which branch / the live DB).

3. Reorganize the file in place into these sections (drop chronological noise,
   keep substance; group by topic, not by timeline):
   - **Session** — date, branch(es), one-line scope.
   - **What was done** — each feature / fix / change with its key files and a
     one-line what + why. Every commit in the range must be reflected here.
   - **Decisions** — choices made and the reason, especially ones a future session
     should not re-litigate. Cross-reference `docs/DECISIONS_NEEDED.md` if logged.
   - **What I learned** — root causes, gotchas, and project-specific facts worth
     keeping (framework/browser behavior, data findings, deploy quirks).
   - **Verification** — how each change was checked (tests / browser / live app),
     and honestly state anything NOT verified.
   - **Still to do / open items** — follow-ups, deferred work, known limitations,
     anything left unfinished.

4. Verify the summary is complete and accurate before finishing:
   - Every commit in the session range appears under "What was done".
   - Every non-trivial decision has a stated reason.
   - "Still to do" is not empty by default — if nothing remains, say so explicitly
     ("No open items").
   - Flag any gap: work done but not summarized, or a summary claim not backed by a
     commit or change. Resolve the gap rather than shipping the summary with it.

5. Recap to the user: the file path and the "Still to do" list. Commit the session
   log with (or alongside) the session's work; if it is the only pending change,
   say so.
