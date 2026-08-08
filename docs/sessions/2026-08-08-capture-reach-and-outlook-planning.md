# Session — 2026-08-08 — capture reach: Outlook integration and phone capture

**Branch:** `worktree-capture-reach-planning`.
**Mode:** planning only. No application code changed this session.
**Scope:** establish why the system is not being used, and turn the user's two stated
needs (home/phone capture, Outlook integration) into a decision set and a task list.

---

## Why this session exists

The user asked for a planner: hold the product context, the architecture, and the real
state of the code, judge what can and cannot be built, and translate needs into
actionable tasks for other agents.

Their two stated needs, verbatim:

1. "I sometimes have things come up in my airgapped env, and sometimes at home (then i
   only have my phone). This will interrupt with the GTD methodology and philosophy
   where everything should come down to a single IN tray."
2. "I work with outlook at work (in the airgapped env). Could we integrate somehow with
   outlook (maybe outlook shortcut for putting an email in the inbox in the gtd-manager
   and automatically translating a scheduled task in the gtd-manager to an outlook
   event?"

---

## State of the system as found

- Phases 1–6 complete; Phase 7 (hardening) not started. 186 tests passing.
- `gui-modernize` is **identical to `master`** — no divergence, tree clean.
- The app was **not running** on ports 8000/8080/5000 on the home machine.

### Home dev database contents (inspected 2026-08-08)

| Table | Rows |
|---|---|
| `capture_inboxitem` | 36 (≈33 are dev mash: "sadjlkasd", "ABCD") |
| `gtd_nextaction` | 16 |
| `gtd_project` | 2 |
| `gtd_waitingfor` | 4 |
| `gtd_somedaymaybe` | 3 |
| `gtd_person` | 4 |
| `reviews_dailyreview` | 1 |
| `reviews_weeklyreview` | 0 |
| areas / contexts / meetings / agenda | 0 |

Last activity 2026-07-18. The only genuine captures are three Hebrew items from that
date (צבא / פסיכולוג / רופא שיניים); **two were never processed**.

**Correction recorded:** this is the *home development* database. The user confirmed a
separate instance runs on the air-gapped work PC, whose data has never been inspected.
The "the system is unused" inference drawn from these numbers is therefore **not
supported** for the real deployment. It is retained here only as dev-instance fact.

---

## Findings that changed the plan

### 1. The premise "GTD requires a single IN tray" is half wrong

GTD requires as few in-baskets as you can get away with, and that they are all **emptied
regularly into one place**. What breaks the system is multiple *lists you must track* —
not multiple *buckets you collect into*. The single-point requirement applies to
**clarifying and tracking**, not to capture.

Consequence: the home/phone problem does **not** require a sync engine across an air gap
(which would be impossible and contradicts the documented out-of-scope list). It requires
a fast way to empty a phone bucket, plus a review step that guarantees it happens.

### 2. Reach is not the blocker at work — friction is

The user confirmed gtd-manager **is running and available** on the air-gapped work PC,
and they still do not capture into it. This rules out "the app isn't there" and points at
switching cost: the work happens in Outlook, and capture requires leaving Outlook.

Both requested features are the same underlying fix: **bring capture to where the user
already is.** That makes Outlook integration an adoption fix, not a convenience feature.

### 3. The air-gap constraint does NOT block Outlook integration

gtd-manager and Outlook run on the **same Windows machine**. Talking to a local Outlook
is local IPC, not a call to an external host, so the `docs/AIR_GAP_DEPLOYMENT.md`
constraint is not violated. This was the key feasibility question and the answer is
favourable.

### 4. Unverified risk — Hebrew / RTL

Every template is hardcoded `lang="en"`. Grep found **no `dir` attribute and no RTL CSS
anywhere** in `templates/` or `static/css/app.css`. The user's only real captures are
Hebrew. Mixed Hebrew/English rendering has not been confirmed in a browser — a launch
attempt was interrupted. If capture mangles their text, that is an adoption blocker
independent of everything above.

---

## Feasibility assessment

### Email → GTD inbox

| Approach | Mechanism | Verdict |
|---|---|---|
| **A. Outlook folder pull (preferred)** | User drags mail to a "GTD" folder; app pulls via COM (`pywin32`) on demand or timer | Needs no macros, opens no HTTP endpoint. Most robust to corporate lockdown. Captures subject, sender, body, and `EntryID` for a link back |
| **B. VBA ribbon button** | Macro POSTs selected mail to `127.0.0.1` | One-click and instant, but requires macros permitted **and** a local API endpoint (currently out of scope) |
| **C. Macro → drop folder** | Macro writes a file; app ingests it | Middle ground; no network surface |

**Blocking unknown:** "New Outlook" and Outlook on the web have **no COM interface**.
Classic Outlook desktop does. This single fact decides whether A is available at all.

### `scheduled_for` → Outlook calendar event

Feasible one-way, on demand, via the same COM channel.

**GTD guardrail:** map **`scheduled_for` only**. Never `deadline`, never `defer_until`.
`scheduled_for` is defined in the domain model as "must occur on this specific
date/time", which is exactly the calendar's hard landscape; `deadline` is an external
commitment, not a time to work, and pushing it to the calendar would convert the calendar
into a task list — the classic GTD failure. Stamp the NextAction id into the event so a
later reconcile stays possible. Two-way sync is explicitly **not** recommended now.

### Home / phone capture

Confirmed need is **capture only** — no list review at home. The user reports a transfer
path exists and would be used from their phone; the exact channel is still unknown.

If that channel is "email myself at work", home capture collapses into the **same Outlook
pull pipeline** as everything else — one mechanism serving both needs. This is the
outcome to aim for.

Independently useful regardless of channel: **bulk paste capture** (paste N lines → N
inbox items) plus an explicit bucket-emptying step in the daily/weekly review.

---

## Scope collisions — user decision required, do not build past these

`docs/PRODUCT_REQUIREMENTS.md` §1 currently lists as out of scope for MVP:

- "Email or calendar integration" — directly contradicted by need 2
- "API endpoints" — contradicted by approach B only
- "Synchronization across devices or accounts" — arguably touched by need 1

Per `CLAUDE.md`, `PRODUCT_REQUIREMENTS.md` changes only if requirements genuinely change.
They now have. The correct path is an **explicit scope amendment plus an ADR**, not
silent implementation. New dependency `pywin32` would also require a wheelhouse doc
update in `docs/AIR_GAP_DEPLOYMENT.md`.

---

## Open questions blocking the build

1. **Which Outlook client** at work — Classic desktop (COM available) vs New Outlook/web
   (no COM). Decisive for approach A.
2. **Are VBA macros / COM automation permitted** by policy, and are the Trust Center
   controls greyed out (= group-policy locked)?
3. **What is the home→work transfer channel**, concretely? Whether it is "email myself"
   determines if one pipeline can serve both needs.
4. **Why is capture not happening at work** when the app is running and available? The
   switching-cost hypothesis is unconfirmed.
5. **Does Hebrew text render correctly** in capture, the Next Actions list, and clarify?

Checks 1–2 were written up and handed to the user to run at work.

---

## Draft task list (provisional — gated on the questions above)

Written with user-observable outcomes, per the verification discipline in `CLAUDE.md`.

| # | Task | Observable outcome | Gate |
|---|---|---|---|
| 1 | Verify Hebrew/RTL rendering | A Hebrew item reads correctly in the capture bar, Next Actions list, and clarify screen — in a browser, both themes | none |
| 2 | Bulk paste capture | Pasting 8 lines into one box produces 8 separate inbox items | none |
| 3 | Bucket-emptying review step | The daily review explicitly asks whether outside buckets are empty, and cannot be completed silently without it | none |
| 4 | Scope amendment + ADR | `PRODUCT_REQUIREMENTS.md` reflects the new integration scope; an ADR records the decision and rejected alternatives | user decision |
| 5 | Outlook folder pull | Moving a mail to the "GTD" folder and clicking "Pull from Outlook" creates an inbox item with subject, sender, and a working link back | Q1, Q2 |
| 6 | `scheduled_for` → calendar push | Setting a scheduled time on an action creates an Outlook appointment at that time; deadlines and defer dates create nothing | Q1, Q2 |
| 7 | Wheelhouse update for `pywin32` | Air-gap deployment doc lists the new dependency and its transfer procedure | after 5 |

Task 1 is first because it is cheap, unblocked, and could invalidate the assumption that
the app is usable in the user's own language.

---

## Notes for the next session

- Live `db.sqlite3` was **never modified**. A copy was made to the job tmp dir for a
  browser probe, had a throwaway password set on the copy only, and was deleted unused.
- `.claude/skills/verify/SKILL.md` forbids creating users or resetting the real
  password. Browser verification of the running app still needs either the user's
  credentials or the disposable-copy approach described above.
- The work instance's database has never been seen. Any future adoption claim must be
  based on it, not on the home dev DB.
