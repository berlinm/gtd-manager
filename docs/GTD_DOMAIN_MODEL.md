# GTD Domain Model

## 1. Entities

### InboxItem

Raw capture. Disappears from the active inbox view after clarification but
the record is retained with a disposition.

| Field | Type | Notes |
|---|---|---|
| `title` | string | Required |
| `body` | text | Optional |
| `captured_at` | datetime | Set on creation |
| `processed_at` | datetime | Null until clarified |
| `disposition` | enum | See values below |
| `content_type` | FK (ContentType) | Generic FK — null if no object created |
| `object_id` | integer | Generic FK — null if no object created |

**Disposition values:** `pending`, `trashed`, `done_immediately`, `delegated`,
`action_created`, `project_created`, `someday_created`, `reference_created`

---

### Project

An outcome requiring more than one action. The title must state what "done"
looks like, not a topic.

| Field | Type | Notes |
|---|---|---|
| `title` | string | Should state a desired outcome |
| `desired_outcome` | text | Longer description of what "done" looks like |
| `status` | enum | `active`, `on_hold`, `completed`, `cancelled` |
| `on_hold_reason` | text | Required when status is `on_hold` |
| `area` | FK (AreaOfResponsibility) | Nullable |
| `deadline` | date | Nullable; real external deadline for the outcome as a whole |
| `created_at` | datetime | Set on creation |
| `completed_at` | datetime | Null unless status is `completed` or `cancelled` |
| `last_reviewed_at` | datetime | Null until first review |
| `next_review_on` | date | Nullable; meaningful primarily for on-hold projects |
| `last_activity_at` | datetime | Derived — see note below |

**`last_activity_at`:** The most recent `updated_at` or `completed_at` across
the project's associated next actions and waiting-for items. Implementation
strategy (denormalized field vs. computed annotation) is TBD.

**Project deadline vs. action deadline:** `Project.deadline` represents the
real external deadline for the project outcome as a whole. It is not equivalent
to the `deadline` on any particular action within the project. A project may
have a deadline even if none of its current actions do; actions may have
deadlines independent of the project deadline.

**Stuck project:** A derived state, not a status field. An active project with
no `active` NextActions and no `waiting` WaitingFor items is stuck. On-hold
projects are never stuck (they have an explicit reason).

---

### NextAction

A concrete, physical action. Never carries a `delegated_to` field. Never has
a `delegated` status. Delegation is handled by creating a WaitingFor item and
cancelling this action.

| Field | Type | Notes |
|---|---|---|
| `title` | string | Required |
| `body` | text | Optional |
| `project` | FK (Project) | Nullable — standalone actions have no project |
| `area` | FK (AreaOfResponsibility) | Nullable |
| `contexts` | M2M (Context) | Zero or more contexts |
| `defer_until` | date | Nullable — see date semantics |
| `scheduled_for` | date or datetime | Nullable — see date semantics |
| `deadline` | date | Nullable — see date semantics |
| `status` | enum | `active`, `done`, `cancelled` |
| `created_at` | datetime | Set on creation |
| `completed_at` | datetime | Null unless status is `done` or `cancelled` |

---

### WaitingFor

A first-class delegated commitment. Structurally separate from NextAction.
Does not appear in next-action lists or context-filtered action views.

| Field | Type | Notes |
|---|---|---|
| `title` | string | Required |
| `body` | text | Optional |
| `person` | FK (Person) | Required |
| `project` | FK (Project) | Nullable |
| `delegated_at` | date | When the commitment was handed off |
| `expected_by` | date | Nullable — when the other person is expected to deliver |
| `follow_up_on` | date | Nullable — when the user plans to check in |
| `last_follow_up_at` | date | Nullable — when the user last followed up |
| `result_notes` | text | Nullable — populated when received or closed |
| `status` | enum | `waiting`, `received`, `cancelled` |
| `created_at` | datetime | Set on creation |
| `completed_at` | datetime | Null unless status is `received` or `cancelled` |

**`expected_by` vs. `follow_up_on`:** These are independent fields.
`expected_by` is the delivery date the other person is working toward.
`follow_up_on` is the date on which the user plans to reach out if nothing has
been received. `follow_up_on` is typically earlier than `expected_by`. No
constraint forces `follow_up_on` < `expected_by`, but the UI must display both
clearly.

---

### AgendaItem

A topic queued for a specific conversation. Not a next action. No date fields.

| Field | Type | Notes |
|---|---|---|
| `title` | string | Required |
| `body` | text | Optional |
| `person` | FK (Person) | Nullable — exactly one of person or meeting must be set |
| `meeting` | FK (Meeting) | Nullable — exactly one of person or meeting must be set |
| `project` | FK (Project) | Nullable |
| `created_at` | datetime | Set on creation |
| `resolved_at` | datetime | Null until marked resolved |

**XOR constraint:** `person` and `meeting` are mutually exclusive. Exactly one
must be set; both null and both set are invalid. Enforced in `clean()`.

---

### Person

A lightweight contact record used by WaitingFor and AgendaItem.

| Field | Type | Notes |
|---|---|---|
| `name` | string | Required |
| `notes` | text | Optional context |
| `active` | boolean | Inactive persons are hidden from selection |

---

### Meeting

A recurring agenda target. Not a one-time event — that is MeetingSession.

| Field | Type | Notes |
|---|---|---|
| `title` | string | e.g., "Weekly team standup", "1:1 with manager" |
| `notes` | text | Optional context |
| `active` | boolean | |

---

### MeetingSession

One particular occurrence of a recurring Meeting.

| Field | Type | Notes |
|---|---|---|
| `meeting` | FK (Meeting) | Required |
| `occurred_on` | date | Required |
| `start_time` | time | Nullable |
| `end_time` | time | Nullable |
| `notes` | text | Optional free-text summary of the session |
| `closed_at` | datetime | Null until the session is marked finished |

When `closed_at` is set, unprocessed MeetingNotes for that session become
visible in a processing queue analogous to the inbox.

---

### MeetingNote

A raw note captured during a MeetingSession. Requires no classification while
the meeting is occurring. Processed afterward like an InboxItem.

| Field | Type | Notes |
|---|---|---|
| `session` | FK (MeetingSession) | Required |
| `title` | string | Required |
| `body` | text | Optional |
| `captured_at` | datetime | Set on creation |
| `processed_at` | datetime | Null until clarified |
| `disposition` | enum | Same values as InboxItem.disposition |
| `content_type` | FK (ContentType) | Generic FK — null if no object created |
| `object_id` | integer | Generic FK — null if no object created |

**A MeetingNote may be processed into:** NextAction, WaitingFor, Project,
AgendaItem, Reference, or no action (trashed / done immediately).

---

### SomedayMaybe

An incubated idea. Not an active commitment. Invisible to action lists and
stuck-project detection.

| Field | Type | Notes |
|---|---|---|
| `title` | string | Required |
| `body` | text | Optional |
| `area` | FK (AreaOfResponsibility) | Nullable |
| `created_at` | datetime | Set on creation |
| `reviewed_at` | datetime | Updated during weekly review |
| `promoted_at` | datetime | Null unless promoted to a project |
| `promoted_to_project` | FK (Project) | Null unless promoted |

---

### Reference

Non-actionable information. No action fields.

| Field | Type | Notes |
|---|---|---|
| `title` | string | Required |
| `body` | text | Required |
| `tags` | M2M (Tag) | For organization and search |
| `area` | FK (AreaOfResponsibility) | Nullable |
| `created_at` | datetime | Set on creation |
| `updated_at` | datetime | Updated on save |

Reference has no `deadline`, `defer_until`, `scheduled_for`, or `status` field.

---

### AreaOfResponsibility

An ongoing standard to maintain. Not a temporary outcome (that is a Project).

| Field | Type | Notes |
|---|---|---|
| `title` | string | Required |
| `description` | text | Optional |
| `active` | boolean | |

---

### Context

A filter tag for NextActions. Represents where or with what an action can be done.

| Field | Type | Notes |
|---|---|---|
| `label` | string | e.g., `@phone`, `@computer`, `@errands` |
| `active` | boolean | Inactive contexts hidden from selection |

---

### Tag

Used only by Reference. Distinct from Context.

| Field | Type | Notes |
|---|---|---|
| `label` | string | Required |

---

### WeeklyReview

A timestamped record of a completed weekly review.

| Field | Type | Notes |
|---|---|---|
| `completed_at` | datetime | When the review was finished |
| `notes` | text | Optional |
| `inbox_cleared` | boolean | Whether inbox reached zero |
| `stuck_projects_acknowledged` | boolean | Whether stuck projects were addressed |

---

### DailyReview

A timestamped record of a completed daily review. The focus selection produced
during the review is transient and is not stored as a permanent artifact.

| Field | Type | Notes |
|---|---|---|
| `completed_at` | datetime | When the review was finished |
| `notes` | text | Optional |
| `focus_cleared_at` | datetime | Null until the user explicitly clears the focus selection |

**Focus list storage strategy:** TBD. Options include Django's session store, a
short-lived model with expiry, or a temporary database table cleared on review
completion. The chosen mechanism must ensure the focus list does not persist
beyond the daily review session or an explicit clear action.

---

## 2. Relationships

```
AreaOfResponsibility 1──* Project
AreaOfResponsibility 1──* NextAction  (standalone actions)
AreaOfResponsibility 1──* SomedayMaybe
AreaOfResponsibility 1──* Reference

Project 1──* NextAction
Project 1──* WaitingFor
Project 1──* AgendaItem
Project.deadline   (field — project-level external deadline)

Person 1──* WaitingFor
Person 1──* AgendaItem  (mutually exclusive with Meeting per item)

Meeting 1──* MeetingSession
Meeting 1──* AgendaItem  (mutually exclusive with Person per item)
MeetingSession 1──* MeetingNote

SomedayMaybe ──(promoted to)──> Project  (optional; FK on SomedayMaybe)

NextAction *──* Context
Reference  *──* Tag

InboxItem    ──(generic FK)──> NextAction | Project | WaitingFor |
                                SomedayMaybe | Reference | (none)
MeetingNote  ──(generic FK)──> NextAction | Project | WaitingFor |
                                AgendaItem | Reference | (none)
```

---

## 3. Status Lifecycles

### Project

| From | To | Requirement |
|---|---|---|
| `active` | `on_hold` | `on_hold_reason` must be provided |
| `on_hold` | `active` | `on_hold_reason` cleared; `next_review_on` cleared |
| `active` | `completed` | `completed_at` set |
| `active` | `cancelled` | `completed_at` set |
| `on_hold` | `cancelled` | `completed_at` set |

### NextAction

| From | To | Notes |
|---|---|---|
| `active` | `done` | `completed_at` set |
| `active` | `cancelled` | `completed_at` set; if delegated, WaitingFor already exists |

### WaitingFor

| From | To | Notes |
|---|---|---|
| `waiting` | `received` | `completed_at` set; `result_notes` populated if applicable |
| `waiting` | `cancelled` | `completed_at` set |

### SomedayMaybe promotion

When promoted: a Project is created, `promoted_at` is set, and
`promoted_to_project` FK is populated. The SomedayMaybe record is retained.

### MeetingSession

When `closed_at` is set, unprocessed MeetingNotes for that session enter a
processing queue analogous to the inbox.

---

## 4. Date Semantics

### NextAction — three separate date fields

| Field | Meaning | List behavior |
|---|---|---|
| `defer_until` | Action is not available before this date | Hidden from default next-actions list; visible in a "deferred" section of the project view |
| `scheduled_for` | Action must occur on this specific date (or at this time) | Appears in the Today view on that date; shown in "scheduled" section of project view |
| `deadline` | Must be completed no later than this date | Displayed with urgency; surfaced in daily and weekly review |

A single action may carry any combination of these three fields.

### Chronological validation (enforced in model clean())

- If both `defer_until` and `scheduled_for` are set: `scheduled_for` ≥ `defer_until`
- If both `scheduled_for` and `deadline` are set: `deadline` ≥ `scheduled_for`
- If both `defer_until` and `deadline` are set: `deadline` > `defer_until`

Violations produce explicit validation errors. The application must never
silently ignore an invalid chronological combination.

### WaitingFor date fields

| Field | Meaning |
|---|---|
| `delegated_at` | When the commitment was handed off |
| `expected_by` | The date by which the other person is expected to deliver |
| `follow_up_on` | The date on which the user plans to reach out |
| `last_follow_up_at` | When the user last actively followed up |

`expected_by` and `follow_up_on` are independent. `follow_up_on` is typically
earlier than `expected_by`.

### Project deadline

`Project.deadline` is the real external deadline for the project outcome as a
whole. It is not equivalent to the `deadline` on any particular action within
the project.

---

## 5. Validation Rules

All rules enforced in Django model `clean()` methods.

| Rule | Entity |
|---|---|
| If `defer_until` and `scheduled_for` both set: `scheduled_for` ≥ `defer_until` | NextAction |
| If `scheduled_for` and `deadline` both set: `deadline` ≥ `scheduled_for` | NextAction |
| If `defer_until` and `deadline` both set: `deadline` > `defer_until` | NextAction |
| `person` XOR `meeting` must be set (exactly one, not both, not neither) | AgendaItem |
| `on_hold_reason` required when `status == 'on_hold'` | Project |
| `completed_at` must be set iff status is `completed` or `cancelled` | Project |
| `completed_at` must be set iff status is `done` or `cancelled` | NextAction |
| `completed_at` must be set iff status is `received` or `cancelled` | WaitingFor |
| `promoted_to_project` must be set iff `promoted_at` is set | SomedayMaybe |

---

## 6. Project View: Action Grouping

A project may have multiple active NextActions. The project detail view groups
them:

- **Available now** — active actions with no `defer_until`, or where `defer_until` has passed
- **Deferred** — active actions where `defer_until` is a future date
- **Scheduled** — active actions with a `scheduled_for` date

A project with only deferred or scheduled actions is not stuck. The grouping
makes it clear whether any action is currently available without misrepresenting
the project's state.

---

## 7. Agenda Item Routing

An AgendaItem belongs to exactly one of:

- A **Person** — for 1:1 conversations and ad-hoc contacts
- A **Meeting** — for recurring meetings and team sessions

It may additionally belong to a Project. The agenda view renders two sections:
"By person" and "By meeting." A Meeting entity is a lightweight record (title
and notes only) that groups agenda items the same way a Person does.
