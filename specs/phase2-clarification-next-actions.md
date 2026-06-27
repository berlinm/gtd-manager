# Feature Specification: Phase 2 — Clarification Workflow and Next Actions

**Status:** Approved  
**Phase:** 2  
**Date:** 2026-06-27

---

## Goal

Allow the user to process inbox items into the correct GTD destination through
a fast single-page clarification workflow, and then manage next actions and
projects through their full lifecycle.

---

## User Stories

> As the user, I want to open an inbox item and answer a short decision tree
> so that each item ends up in the right GTD list without unnecessary clicks.

> As the user, I want to see all my next actions filtered by context so that
> I can act on what is available right now.

> As the user, I want to see a project list that flags stuck projects so that
> I always know when a project has no forward movement.

---

## Functional Requirements

### Clarification workflow
1. Each unprocessed inbox item has a "Process" link that opens the clarify page.
2. The clarify page presents the GTD decision in one form: actionable or not,
   then the appropriate sub-choice.
3. Submitting the form creates the target object, stamps `processed_at` and
   `disposition` on the InboxItem, and redirects back to the inbox.
4. "Do it now (< 2 min)" sets disposition `done_immediately` with no object
   created.
5. "Trash" sets disposition `trashed` with no object created.
6. "Someday/maybe" creates a SomedayMaybe (stub — full UI in Phase 3).
7. "Reference" creates a Reference (stub — full UI in Phase 4).
8. "Delegate" creates a WaitingFor (stub — full UI in Phase 3).
9. "Single action" creates a NextAction.
10. "Project" creates a Project and an associated first NextAction.

### NextAction
11. Next actions can be created, edited, and marked done or cancelled.
12. Each next action may have: contexts, project, area, `defer_until`,
    `scheduled_for` (datetime), `deadline`, body.
13. All three chronological validation rules are enforced on save.
14. The next-actions list shows only active actions where `defer_until` is
    null or in the past. Deferred actions are hidden from this list.
15. The list is filterable by context.
16. Completed and cancelled actions are accessible from a separate archive view.

### Project
17. Projects can be created, edited, and transitioned between statuses.
18. `on_hold_reason` is required when setting status to `on_hold`.
19. The project list shows active and on-hold projects in separate sections.
20. A "stuck" badge appears on any active project with no active next actions
    and no active waiting-for items.
21. The project detail view groups actions: available now / deferred / scheduled.
22. Completing or cancelling a project sets `completed_at`.

### Today view
23. The Today view shows: active actions with `scheduled_for` date = today,
    overdue actions (past `scheduled_for`), and actions/projects with
    `deadline` today or overdue.

---

## Acceptance Criteria

- [ ] Clicking "Process" on an inbox item opens the clarify page
- [ ] All six disposition paths close the inbox item and redirect
- [ ] A newly created NextAction appears in the next-actions list
- [ ] A deferred action (future `defer_until`) does not appear in the
      next-actions list
- [ ] Invalid date combinations (e.g. `scheduled_for` before `defer_until`)
      produce a form error, not a silent save
- [ ] An active project with no active actions shows a "stuck" badge
- [ ] Setting a project to `on_hold` without a reason is rejected
- [ ] The Today view shows actions scheduled for today

---

## Non-Goals

- Full WaitingFor, AgendaItem, SomedayMaybe UI (Phase 3)
- Full Reference UI (Phase 4)
- Meeting capture (Phase 5)
- Weekly/daily review (Phase 6)

---

## Domain Entities Affected

| Entity | Operation |
|---|---|
| `InboxItem` | Update (processed_at, disposition, generic FK) |
| `NextAction` | Create, Read, Update |
| `Project` | Create, Read, Update |
| `SomedayMaybe` | Create (stub from clarify only) |
| `WaitingFor` | Create (stub from clarify only) |

---

## Validation Rules

All from `docs/GTD_DOMAIN_MODEL.md` §5, enforced in model `clean()`:
- `scheduled_for` ≥ `defer_until` (if both set)
- `deadline` ≥ `scheduled_for` (if both set)
- `deadline` > `defer_until` (if both set)
- `on_hold_reason` required when `status == on_hold`
- `completed_at` set iff status is `completed` or `cancelled`

---

## Security Considerations

- All views require login
- All POST requests protected by CSRF
- No unescaped user content rendered in templates

---

## Air-Gap Considerations

- No new vendored JS or CSS assets
- `mistune` (Markdown) added to `requirements.txt` for Reference bodies;
  wheelhouse must be regenerated before air-gap deployment
