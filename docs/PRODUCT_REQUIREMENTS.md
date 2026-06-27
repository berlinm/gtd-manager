# Product Requirements

## 1. Product Boundaries

### In scope (MVP)

- Capture of unprocessed inbox items
- Guided clarification of inbox items into the appropriate GTD list
- Full lifecycle management of:
  - Projects
  - Next Actions
  - Waiting-For items
  - Agenda items
  - Someday/Maybe items
  - Reference material
- Areas of Responsibility as organizational containers
- Meeting session capture with deferred note processing
- Daily Review workflow
- Weekly Review workflow
- Processed inbox item history with disposition records
- Single authenticated user
- All data stored locally in SQLite
- All HTML rendered server-side
- JavaScript used only where server round-trips would be actively harmful

### Out of scope (MVP)

- Other people logging into the application
- Collaborative task assignment workflows
- Sharing data with other users or systems
- Synchronization across devices or accounts
- Mobile-optimized layout
- File attachments or binary storage
- Email or calendar integration
- Notifications or reminders delivered outside the browser
- Natural-language parsing or AI assistance
- API endpoints

> **Note:** Tracking work delegated to other people through WaitingFor is
> **in scope**. What is out of scope is *other people logging in*, collaborative
> assignment workflows, and sharing/synchronization.

### Permanently out of scope (air-gap constraint)

- External CDN resources; all assets must be vendored or inline
- Any runtime call to an external host
- OAuth or third-party authentication
- Telemetry of any kind

---

## 2. GTD Invariants

These are correctness constraints. Violation converts the system into a
generic to-do list.

1. **Inbox must be processable to empty.** The weekly review surfaces an
   unprocessed inbox count as an explicit item. Unprocessed meeting notes from
   closed sessions are treated equivalently.

2. **A stuck project is active with no active next actions and no waiting
   waiting-for items.** This is a derived, computed state — not a status field.
   Stuck projects are flagged on the dashboard and in the weekly review. An
   on-hold project with a reason is not stuck.

3. **WaitingFor is not a NextAction with a tag.** It is a structurally separate
   entity with `person`, `delegated_at`, `expected_by`, `follow_up_on`, and
   `last_follow_up_at` fields. It lives on its own list and does not appear in
   next-action counts or context-filtered action lists.

4. **Deadlines represent real external commitments only.** The `deadline` field
   on an action or project is distinct from scheduling and deferral. The UI must
   not present it as a general priority mechanism. Setting a deadline should
   prompt the user to confirm it is a real external constraint.

5. **A project title should state a desired outcome.** The UI prompts
   accordingly with a label and placeholder that ask for an outcome statement,
   not a topic.

6. **Someday/maybe items are not active commitments.** They must not appear in
   next-action lists, project active counts, today views, stuck-project
   detection, or weekly review overdue counts unless explicitly promoted.

7. **Agenda items are not next actions.** They carry no date fields. They appear
   only in the agenda view for a specific person or meeting.

8. **Completed and cancelled items are archived, not deleted by default.**
   Permanent deletion is a separate, intentional act.

9. **Reference material has no action fields.** Reference entities carry no
   `deadline`, `defer_until`, `scheduled_for`, or `status` field.

10. **Capture must be frictionless.** The inbox entry form requires only a
    title. Meeting note capture requires only a title within an open session.
    All other fields are supplied during clarification.

11. **Delegated work lives in WaitingFor only.** Delegation creates a WaitingFor
    item and cancels the originating action. There is no `delegated` status or
    `delegated_to` field on NextAction.

12. **Processed inbox items and meeting notes are retained.** Their disposition
    and any linked object are preserved for review and audit.

13. **The daily review focus list is transient.** It must not alter the GTD
    classification of any item, persist as a named list, or accumulate across
    days. It is a session-scoped orientation aid.

14. **A project may have multiple active next actions.** There is no single
    designated "the next action." The project view groups actions by availability
    so the user can see what is currently actionable.

---

## 3. Risks of Becoming a Generic To-Do List

These are the specific failure modes that must be actively resisted.

1. **Collapsing WaitingFor into NextAction.** If "add a tag" is the delegation
   mechanism, users lose the enforced person field, delivery date, and follow-up
   date. WaitingFor must remain structurally separate.

2. **Allowing due dates everywhere.** If any item can have a deadline, users
   treat deadlines as priority signals rather than real commitments. Deadline
   fields must not appear on agenda items, reference, or someday/maybe.

3. **Skipping the clarification step.** If users can move inbox items directly
   to a list without passing through the clarification questions, the inbox
   becomes a second task list. The clarification workflow must be the only path
   out of the inbox (except trash/delete).

4. **Projects without desired outcomes.** If the project field is labeled
   "Project name" and accepts anything, users create topic buckets rather than
   outcome statements. Labels and placeholders must prompt for outcomes.

5. **Treating Someday/Maybe as a low-priority task list.** If someday/maybe
   items appear in next-action counts or overdue warnings, they cease to be
   incubation.

6. **Burying stuck projects.** The stuck-project flag must be visible on the
   dashboard and in the weekly review.

7. **Merging defer_until, scheduled_for, and deadline into one field.** This is
   the most common GTD implementation error. All three are separate fields with
   separate semantics.

8. **Making capture require categorization.** If the capture form has dropdowns
   for project, context, or type, users either skip capturing or spend cognitive
   load categorizing prematurely.

9. **Conflating Areas of Responsibility with Projects.** Areas are ongoing
   standards to maintain (not completed); projects are temporary outcomes to
   achieve.

10. **Omitting the weekly review workflow.** The weekly review is the mechanism
    that keeps all lists trustworthy.
