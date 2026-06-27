# Feature Specification: [Feature Name]

**Status:** Draft | In Review | Approved | Implemented  
**Phase:** [Roadmap phase this belongs to]  
**Date:** YYYY-MM-DD

---

## Goal

One or two sentences stating what this feature accomplishes and why it matters
to the user. Focus on the outcome, not the implementation.

---

## User Story

> As the user, I want to [action] so that [outcome].

---

## Functional Requirements

A numbered list of what the feature must do. Each item should be testable.

1.
2.
3.

---

## Acceptance Criteria

A checklist of conditions that must all be true for the feature to be considered
complete. Written from the user's perspective.

- [ ]
- [ ]
- [ ]

---

## Non-Goals

What this feature explicitly does not do. This section prevents scope creep
and documents intentional omissions.

- This feature does not...
- This feature does not...

---

## Domain Entities Affected

List all domain entities that are created, read, updated, or deleted by this
feature. Reference `docs/GTD_DOMAIN_MODEL.md` for the authoritative field
definitions.

| Entity | Operation | Notes |
|---|---|---|
| `InboxItem` | Create / Read / Update | |
| `NextAction` | | |

---

## Validation Rules

List any validation rules this feature must enforce. For rules already defined
in `docs/GTD_DOMAIN_MODEL.md`, reference them by name rather than restating
them in full. Add only new rules here.

| Rule | Where enforced | Notes |
|---|---|---|
| | Model `clean()` | |
| | Form validation | |

---

## Security Considerations

- Does this feature require authentication? (Yes — all features except login do)
- Does this feature perform any state-changing operations that require CSRF
  protection? (Yes — all POST / PUT / DELETE do)
- Does this feature expose any data that must not be visible to unauthenticated
  users?
- Are there any input fields that could be vectors for injection attacks?
- Does this feature introduce any new static assets? If so, confirm they are
  vendored and contain no external URLs.

---

## Air-Gap Considerations

- Does this feature introduce any new Python dependencies? If so, they must be
  added to `requirements.txt` (pinned) and the wheelhouse must be regenerated
  on a matching build environment.
- Does this feature use any third-party JavaScript or CSS? If so, the files
  must be committed to `static/`.
- Does this feature reference any external URLs in templates, stylesheets, or
  scripts? (Must be: none.)

---

## Automated Tests

List the tests that should be written to verify correctness. Distinguish between
unit tests (model logic, validation rules) and integration tests (view behavior,
form submission).

**Unit tests:**
- [ ] Test that [validation rule] raises a ValidationError when...
- [ ]

**Integration tests (view / form):**
- [ ] Test that a POST to `/...` creates the expected object
- [ ] Test that an unauthenticated request is redirected to login
- [ ]

---

## Manual Acceptance Tests

Step-by-step instructions a human can follow to verify the feature works
correctly in a running application. These complement automated tests and
cover the golden path as well as key edge cases.

**Golden path:**

1. Log in and navigate to [page]
2. [Action]
3. Verify that [expected result]

**Edge cases:**

1. [Edge case description]
   - [Action]
   - Verify that [expected result]
