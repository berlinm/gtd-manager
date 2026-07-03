# UI Refactor Principles

## Purpose

This document defines the UI/UX principles for refactoring the GTD Manager application.

The goal is not to make the application visually fashionable. The goal is to make it:

- Fast enough for constant capture and daily use
- Clear enough to support correct GTD decisions
- Dense enough for professional work
- Calm enough for extended use
- Trustworthy enough that the user can rely on it as an external system

The intended experience is:

> Fast enough for capture, structured enough for control, and quiet enough for thinking.

This document is a design constraint for all user-facing work. Do not redesign the product into a generic task manager, project-management dashboard, or Kanban application.

---

## 1. Design for the GTD workflow

The interface must reflect the actual GTD workflow:

1. Capture
2. Clarify
3. Organize
4. Review
5. Engage

Each screen should have one dominant purpose.

Examples:

- Capture screens should optimize for speed.
- Clarification screens should optimize for decision-making.
- Project screens should show outcome and project health.
- Review screens should restore trust in the system.
- Action lists should optimize for scanning and selection.

Do not expose the database structure directly to the user. Users should work with meaningful concepts, not model names, internal IDs, or implementation details.

---

## 2. Product-level UX principles

### 2.1 Reduce cognitive load

Show only the information required for the current decision.

Do not display every optional field on every form. Use progressive disclosure to reveal fields only when they become relevant.

Examples:

- Initial inbox capture requires only a title.
- Choosing `Waiting For` reveals person, expected date, follow-up date, and project.
- Choosing `Next Action` reveals project, context, defer date, scheduled date, and deadline.
- Choosing `Reference` reveals notes, area, and tags.
- Choosing `Project` reveals the desired outcome and first actions.

The user should never need to mentally filter a large form containing fields that do not apply.

### 2.2 Optimize for repeated use

This is a professional tool that may be used dozens of times each day.

Favor:

- Fast interaction
- Stable placement
- Predictable navigation
- Compact list layouts
- Keyboard support
- Minimal interruption

Avoid unnecessary animations, decorative transitions, large cards, and repeated confirmation dialogs.

### 2.3 Preserve trust

After every action, make it clear:

- What happened
- Where the item moved
- Whether it was saved
- Whether a filter is hiding it
- Whether an item is still unprocessed
- Whether a project is stuck
- Whether a backup or review completed successfully

Never leave the user uncertain about the state of the system.

---

## 3. Visual direction

The application should feel like a calm, professional command center.

### Use

- Neutral page backgrounds
- Clearly separated surfaces
- One primary accent color
- One warning color
- One danger color
- System fonts
- Consistent spacing
- Moderate corner radius
- Subtle borders
- Very subtle shadows, only where hierarchy requires them
- Clear typography hierarchy
- Restrained use of icons
- High-contrast focus indicators

### Avoid

- Glassmorphism
- Large gradients
- Excessive shadows
- Oversized cards
- Decorative dashboard charts
- Too many badge colors
- Large empty spaces that reduce information density
- A different visual language for every entity
- Animation that delays interaction
- Icons without labels where meaning is not obvious

The application should look modern because it is coherent, fast, and well-structured—not because it uses visual effects.

---

## 4. Layout and navigation

### 4.1 Stable application shell

Use a persistent application shell with:

- Left navigation sidebar on desktop
- Main content area
- Consistent page header
- Persistent quick-capture access
- Clear active navigation state

Recommended primary navigation:

- Dashboard
- Inbox
- Next Actions
- Projects
- Waiting For
- Agendas
- Meetings
- Someday / Maybe
- Reference
- Reviews

Secondary navigation may include:

- Areas
- Archive
- Settings
- Backup and Restore

Do not create deeply nested menus. All primary GTD lists should be reachable in one click.

### 4.2 Meaningful counts

Show counts only when they communicate something actionable.

Good examples:

- `Inbox 7`
- `Waiting For 2 due`
- `Projects 3 stuck`
- `Meeting Notes 4 unprocessed`

Avoid showing totals that do not affect a decision.

### 4.3 Page headers

Every page should make three things immediately clear:

1. Where the user is
2. What currently requires attention
3. What the primary action is

A page header should normally contain:

- Page title
- One-line description when needed
- Primary action
- Relevant status or exception count

Do not place multiple equally prominent primary buttons in the same header.

---

## 5. Capture experience

Capture is the highest-frequency interaction and must be nearly frictionless.

### Requirements

- Capture should be accessible from every major screen.
- Provide a global shortcut where practical.
- Title is the only required field.
- `Enter` saves.
- After saving, focus returns to an empty capture field.
- Consecutive capture must not require navigation.
- Show a subtle success confirmation.
- Do not interrupt with a modal after every capture.
- Do not require project, context, date, priority, or type selection.
- Preserve entered text if validation fails.

Recommended initial appearance:

```text
What is on your mind?
[____________________________________________] [Capture]