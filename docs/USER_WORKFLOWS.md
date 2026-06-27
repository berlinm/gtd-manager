# User Workflows

## 1. Capture

A persistent capture bar is visible on every page. The user types a title and
submits. A bare InboxItem is created with only a title and timestamp. No
categorization is required at capture time. Friction at this step actively
harms the GTD system.

During a meeting, the user opens a MeetingSession and captures MeetingNote
records in rapid succession. Notes captured in this context require no
classification until after the meeting ends.

**Rule:** The capture form requires only a title. All other fields are supplied
during clarification.

---

## 2. Clarify (Process)

Inbox items and meeting notes are clarified through a fast guided workflow
presented on a single page. The UI presents these choices with minimal
navigation. A straightforward inbox item should be clarifiable in one
interaction. Only items requiring project setup or complex decomposition
warrant additional steps.

```
Is it actionable?
├── No →
│   ├── Trash (mark disposed as "trashed"; no object created)
│   ├── Someday/Maybe (create SomedayMaybe; disposed as "someday_created")
│   └── Reference (create Reference; disposed as "reference_created")
└── Yes → What is the next physical action?
    ├── < 2 minutes → Do it now
    │   └── Mark disposed as "done_immediately"; no action object created
    ├── Delegate → Create WaitingFor; disposed as "delegated"
    └── Defer →
        ├── Single action → Create NextAction; disposed as "action_created"
        └── Multi-step outcome → Create Project; identify first NextAction
            └── Disposed as "project_created"
```

The InboxItem or MeetingNote record is retained after clarification. Its
`processed_at` timestamp is set, it carries a `disposition` value, and where
applicable a generic foreign key points to the object created from it.
Processed items do not appear in the active inbox or meeting notes views.

---

## 3. Organize

After an item has been clarified, the user may further organize it:

- Assign context tags to next actions (`@phone`, `@computer`, `@errands`, etc.)
- Assign a project to a next action
- Assign an area of responsibility to a project, standalone action,
  someday/maybe item, or reference item
- Set `defer_until` if an action is unavailable before a certain date
- Set `scheduled_for` if an action must occur on a specific date or time
- Set `deadline` on an action only when an external commitment makes that
  date hard
- Set `deadline` on a project when the overall outcome has a real external
  deadline distinct from any individual action deadline
- Assign a Person to a waiting-for item or agenda item
- Assign a Meeting to an agenda item

---

## 4. Daily Review

The daily review is a lightweight, fast workflow intended to start the work day
with orientation. It does not replace the weekly review and does not alter any
GTD classifications.

**Steps:**

1. **Urgent inbox** — scan for newly captured items that need same-day
   clarification; process those only
2. **Scheduled today** — review all next actions with `scheduled_for` = today
3. **Deadlines** — review all actions and projects with a `deadline` today or
   overdue; review any deadline within the next 7 days
4. **Waiting-for follow-ups** — review waiting-for items with
   `follow_up_on` ≤ today
5. **Focus selection** — select a small temporary set of actions to focus on
   today
6. **Identify urgent problems** — surface stuck projects and overdue deadlines
   not already addressed

**Focus list rules:**

- The focus list is a transient UI aid
- It must not create a permanent "Today" category
- It must not modify an action's GTD classification
- It must not appear as a list that accumulates over time
- The focus selection does not persist beyond the daily review session or an
  explicit clear action
- The DailyReview record captures completion timestamp and notes; it does not
  store the focus selection as a permanent artifact

---

## 5. Weekly Review

The primary GTD review. The mechanism that keeps all lists trustworthy.

**Steps:**

1. Process all inbox items to empty; process outstanding meeting notes from
   closed sessions
2. Review active projects: confirm each has at least one active next action or
   active waiting-for item; flag stuck projects
3. Review on-hold projects: decide whether any should be reactivated or have
   their `next_review_on` updated
4. Review project deadlines approaching within the next two weeks
5. Review waiting-for items: identify any with `follow_up_on` ≤ today or no
   `follow_up_on` set
6. Review someday/maybe: promote anything now relevant
7. Review agenda items: drop anything resolved
8. Review upcoming scheduled and deadline items for the coming week
9. Mark review complete (timestamps the WeeklyReview record)

---

## 6. Meeting Capture

1. User creates or selects a Meeting (a recurring agenda target)
2. User opens a new MeetingSession (one occurrence, with date and optional times)
3. During the session, MeetingNote records are created rapidly — title only, no
   classification required
4. Agenda items assigned to this meeting are visible alongside the notes as
   reference during the session
5. After the meeting ends, the user closes the session (`closed_at` set)
6. Unprocessed notes from the closed session enter a processing queue; the user
   processes them through the standard clarification workflow

---

## 7. Engage (Do)

How the user selects and executes work:

- **Next-actions list** — filtered by context and/or area; grouped by
  availability (available now vs. deferred vs. scheduled)
- **Today view** — overdue actions, actions with `scheduled_for` today, deadline
  items due today or overdue
- **Daily review focus list** — transient, session-scoped; not a permanent list
- **Project detail view** — actions grouped by available / deferred / scheduled;
  associated waiting-for items; associated agenda items
- **Waiting-for list** — sorted by `follow_up_on` date
- **Agenda view** — grouped by person and by meeting

---

## 8. Delegation Workflow

When the user decides an active next action should be delegated:

1. Create a new WaitingFor item, supplying:
   - `person` (who it is delegated to)
   - `delegated_at` (today)
   - `expected_by` (when they are expected to deliver)
   - `follow_up_on` (when to check in)
2. Cancel the originating NextAction; note in the cancellation that a
   WaitingFor item was created

The cancelled NextAction is archived. The WaitingFor item is the active record
of the commitment. There is no `delegated` status on NextAction and no
`delegated_to` field on NextAction.

---

## 9. Someday/Maybe Promotion

When a someday/maybe idea becomes actionable:

1. User opens the SomedayMaybe item and selects "Promote to Project"
2. A new Project is created from the item's title and body
3. `SomedayMaybe.promoted_at` is set and `promoted_to_project` FK is populated
4. The SomedayMaybe record is retained; it is no longer active
5. The user immediately identifies the first next action for the project

---

## 10. Processing Inbox History

The user can view all previously processed inbox items and meeting notes,
including:

- What the item was
- When it was captured and processed
- What disposition was assigned
- A link to the object created from it (if any)

This view supports the weekly review and allows the user to recover from
mis-classifications without permanent data loss.
