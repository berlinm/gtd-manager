# Manual Test Plan — GTD Manager

Run through this after any significant change to verify end-to-end behaviour.
Each section lists numbered steps and the expected outcome in **bold**.

## Prerequisites

1. Start the dev server: `.venv\Scripts\python.exe manage.py runserver`
2. Open `http://127.0.0.1:8000/` in a browser.
3. Log in with your superuser account.

---

## 1. Capture bar (every page)

1. Type a thought into the capture bar at the top and press Enter.
   **→ The input clears and "Captured." appears below it.**
2. Click the blue Capture button (leave the input filled).
   **→ Same result.**
3. Check the Inbox count in the nav updates without a page reload.
   **→ The number in `Inbox (N)` increases by one each time.**
4. Capture an item, then navigate to **Inbox** via the nav link.
   **→ The captured item appears in the inbox table.**

---

## 2. Inbox list

1. Navigate to **Inbox**.
   **→ All unprocessed items are listed. Each row has a "Process" button.**
2. Capture several items and confirm they all appear.
3. Process one item (any disposition). Return to Inbox.
   **→ The processed item is gone from the list.**

---

## 3. Clarification — all seven dispositions

For each sub-test: capture a fresh item first, then click **Process**.

### 3a. Trash
1. Click **Trash it**.
   **→ Redirected to Inbox. Item is gone from the list.**

### 3b. Done immediately
1. Click **Done immediately**.
   **→ Redirected to Inbox. Item is gone.**

### 3c. Someday / Maybe
1. Click **Someday / maybe**.
   **→ Redirected to Inbox. Item removed from inbox.**
2. Navigate to **Someday**. **→ The item appears in the list.**

### 3d. Reference
1. Click **Save as reference**.
   **→ Redirected to the new reference detail page. Item removed from inbox.**

### 3e. Delegate (validation)
1. Leave the name field empty in the Delegate fieldset. Click **Create Waiting-For**.
   **→ Error message appears. Item is NOT processed.**

### 3f. Delegate (success)
1. Type a name (e.g. "Alice") in the Delegate fieldset. Optionally select a project. Click **Create Waiting-For**.
   **→ Redirected to the Waiting For list. A new waiting-for item appears with title from the inbox item, person "Alice", and the chosen project (if any).**

### 3g. Action
1. Edit the title in the "Single next action" fieldset if you like. Click **Create Action**.
   **→ Redirected to the Actions list. The new action appears.**

### 3g2. Add action to existing project
1. First ensure at least one active project exists (create one via **Projects → + Add project** if needed).
2. Capture a fresh inbox item and click **Process**.
3. In the "Add action to an existing project" fieldset, select the project from the dropdown. Edit the action title if needed. Click **Add to Project**.
   **→ Redirected to that project's detail page. The new action appears under the project.**
4. Process another inbox item. Leave the project dropdown on "— select a project —". Click **Add to Project**.
   **→ Error message appears. Item is NOT processed.**

### 3h. Project
1. Fill in a project title and first action in the "Project" fieldset. Click **Create Project**.
   **→ Redirected directly to the new project's detail page. The project title and first action are visible.**
2. Leave the first action blank. Click **Create Project**.
   **→ Same redirect. Project detail page shows "No actions yet."**

---

## 4. Next Actions list (`/actions/`)

1. Navigate to **Actions**.
   **→ Active, non-deferred actions are listed.**
2. Create an action with a defer-until date in the future (via **+ Add action**).
   **→ The action does NOT appear in the list.**
3. Create an action with a defer-until date of today.
   **→ The action DOES appear.**
4. If you have Contexts defined, click a context filter link.
   **→ Only actions tagged with that context are shown.**
5. Click **Done** on any action.
   **→ The action disappears from the list.**

---

## 5. Add / Edit action — date validation

1. Open **+ Add action**. Set `defer_until` = today, `deadline` = today.
   **→ Save fails with "Deadline must be after the defer-until date."**
2. Set `defer_until` = today, `scheduled_for` = yesterday.
   **→ Save fails with "Scheduled date cannot be before the defer-until date."**
3. Set all three dates in correct order (defer < scheduled < deadline). Click **Save**.
   **→ Saves successfully.**

---

## 6. Today view (`/actions/today/`)

1. Create an action with `scheduled_for` = now (or any time today). Navigate to **Today**.
   **→ The action appears.**
2. Create an action with `deadline` = today.
   **→ It also appears in Today.**
3. Create a WaitingFor item with `follow_up_on` = today. Navigate to **Today**.
   **→ "Follow-ups due" section appears with the item.**
4. Mark the scheduled action done from the Today page.
   **→ It disappears from the list.**

---

## 7. Projects list (`/projects/`)

1. Navigate to **Projects**.
   **→ Active projects are listed. On-hold projects in a separate section.**
2. A project with no actions shows the **stuck** badge.
3. Add an action to a stuck project. Return to Projects.
   **→ The stuck badge is gone.**
4. Edit a project → set status to **On hold** without filling the reason.
   **→ Save fails with a validation error.**
5. Set status to On hold with a reason.
   **→ Saves. Project moves to the On hold section.**

---

## 8. Project detail

1. Open any project.
   **→ Actions are grouped: Available now / Deferred / Scheduled.**
2. Any WaitingFor items linked to the project appear in a "Waiting for" section.
3. Click **+ Add action** from the detail page.
   **→ The new action form has this project pre-selected.**
4. Click **Done** on an action from the project detail page.
   **→ The action disappears. If it was the last one, the project shows "No actions yet."**

---

## 9. Waiting For (`/waiting/`) and history

1. Navigate to **Waiting**. Items with `follow_up_on` ≤ today are **highlighted**.
2. Click **Received** on an item that is NOT linked to a project. Optionally add result notes.
   **→ Redirected to Waiting list. The item is gone.**
3. Click **Received** on an item that IS linked to a project.
   **→ Redirected to that project's detail page** (so you can immediately add a follow-up action if needed).
4. Edit a waiting-for item. Assign it to a project using the **Project** dropdown. Save.
   **→ Item appears in the project's detail page under "Waiting for".**
5. Edit a waiting-for item. Change the follow-up date to tomorrow. Save.
   **→ Highlight is gone.**
6. Click **History** on the Waiting For page.
   **→ All received and cancelled items are listed with their result notes, person, project (if any), and completion date.**
7. Open a project that had a delegation received. Go to the project detail.
   **→ A "Received" section appears below "Waiting for", showing the item, person, date, and result notes.**

### 9a. Delegate from an action
1. Open any active action via **Edit**.
2. Click **Delegate…**.
   **→ Pre-filled form shows the action's title.**
3. Choose a person and submit.
   **→ Redirected to Waiting list. New item is there. The original action is cancelled (gone from Actions list).**

---

## 10. Agenda (`/agenda/`)

1. Navigate to **Agenda**.
2. Click **+ Add item**. Choose a person (leave meeting blank). Save.
   **→ Item appears under "By person" → the person's name.**
3. Add another item for a meeting. **→ Appears under "By meeting".**
4. Try to save an item with both person AND meeting filled.
   **→ Validation error: "Choose either a person or a meeting, not both."**
5. Try to save with neither filled.
   **→ Validation error: "Choose a person or a meeting."**
6. Click **Raised** on an item.
   **→ Item is deleted from the agenda.**

---

## 11. Someday / Maybe (`/someday/`)

1. Navigate to **Someday**. Items captured from inbox or added directly appear here.
2. Click **Activate** on an item.
   **→ Pre-filled form with the idea's title.**
3. Fill in a project title and first action. Click **Create project**.
   **→ Redirected to the new project detail page.**
4. Return to Someday.
   **→ The promoted item is gone from the list.**

---

## 12. Areas of responsibility (`/settings/areas/`)

1. Go to `/settings/areas/`. Click **+ Add area**.
2. Create an area (e.g. "Work").
   **→ Appears in the list.**
3. Open **Add project**. The area dropdown now shows "Work".
4. Create a project with that area. Open the project detail.
   **→ The area name appears next to the status badge.**

---

## 13. Dashboard

1. Navigate to **Dashboard**.
   **→ Inbox count, Waiting For follow-ups due, and stuck project count are shown.**
2. Process all inbox items → Inbox shows "Inbox is empty."
3. Create a stuck project → Projects card shows stuck count.

---

## 14. Dark / light mode

1. Click the ☀ button in the nav.
   **→ Page switches to dark mode. Icon changes to ☽.**
2. Reload the page.
   **→ Dark mode is preserved (stored in localStorage).**
3. Click ☽ again.
   **→ Back to light mode.**

---

## 15. Reference (`/reference/`)

1. Navigate to **Reference**. Click **+ Add**. Fill in a title and body using Markdown:
   ```
   ## Heading
   - bullet one
   - bullet two
   ```
   Click **Save**.
   **→ Redirected to the reference detail page. Body is rendered as HTML (heading + list visible).**

2. Clarify an inbox item as "file as reference". Click **Save as Reference**.
   **→ Redirected directly to the new reference detail page (not back to inbox).**

3. Go to **Reference**. Type a word from the body in the search box. Click **Search**.
   **→ Only items whose title or body contain that word are shown.**

4. Search for a word that matches nothing.
   **→ "No results for…" message shown.**

5. Edit a reference. Change the body. Save.
   **→ The updated content is shown on the detail page. "Updated" date has changed.**

---

## 16. Area detail (`/areas/<pk>/`)

1. Create an area at `/settings/areas/`. Click its name in the list.
   **→ Area detail page opens showing "Nothing assigned to this area yet."**

2. Create a project and assign it to the area. Return to the area detail.
   **→ Project appears under "Active projects".**

3. Create a next action (no project) assigned to the area.
   **→ Appears under "Standalone actions".**

4. Create a reference assigned to the area.
   **→ Appears under "Reference".**

5. Put the project on hold. Reload area detail.
   **→ Project moves to "On hold" section.**

---

## 17. Inbox history (`/inbox/history/`)

1. Click **History** on the inbox page.
   **→ All processed items are listed with their disposition label (e.g. "Action created", "Delegated").**

2. An item processed as "action" shows a clickable **Action** link in the Created column.
   **→ Link opens the action edit page.**

3. An item processed as "project" shows a **Project** link → opens the project detail.

4. An item processed as "trash" or "done immediately" shows no link in the Created column (nothing was created).

5. If you have more than 50 processed items, pagination controls appear.

---

## 18. Authentication

1. Log out via the **Log out** button.
   **→ Redirected to login page.**
2. Try to navigate to `/inbox/` directly.
   **→ Redirected to login page (not a 500 or 403).**
3. Log back in.
   **→ Redirected to Dashboard.**
