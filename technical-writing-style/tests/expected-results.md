# Expected results

Accepted forms are examples. Different wording passes when it follows the same rule and keeps the same meaning.

## docs-sample.md (documentation mode)

The report's first line should name documentation mode and give the reason (a Markdown file with headings and a procedure).

### Must change

| Item | Accepted forms | Rule |
| --- | --- | --- |
| Title and the three headings in title case | Sentence case. The task headings may also change to a verb: "Configure notifications for shared projects," "Turn on notifications." | Capitalize. Documentation: headings |
| "In today's fast-paced digital world, teams need to stay informed." | Deleted | Machine tells: openers that announce |
| "This section explains how to configure notifications for shared projects." | Deleted. The heading already carries "shared projects." | Documentation: cut the fluff |
| Em dash in "when a task changes — for example" | A comma, a period, or parentheses | Punctuate: no em dashes |
| Semicolon in "commented on; you can also" | Two sentences | Punctuate: no semicolons |
| "The user must have the Admin role." | "You need the Admin role." or "You must have the Admin role." | Address the reader |
| "Please note that" | Deleted. The rest of the sentence stays negative. | Prose: cut needless words. Limit: a scope exclusion stays negative. |
| "Click on Settings > Notifications." | "Select **Settings** > **Notifications**." | Interaction verbs. Documentation: UI labels |
| 'Check the box labeled "Email me when a task is assigned to me"' | "Select the **Email me when a task is assigned to me** checkbox." with a period. The label text is copied exactly. | Documentation: UI labels. Procedures: full sentences |
| "(e.g. Instant, Hourly, Daily)" | "(for example, Instant, Hourly, Daily)" or "(such as Instant, Hourly, Daily)" | Words table: Latin abbreviations |
| Step 4, "Changes are saved automatically in near real time." | Moved out of the numbered list as a result sentence or a note. The fact is kept. | Documentation: procedures. A step that isn't an action |
| "15 notification types are supported; the most important are listed below:" | "Fifteen notification types are supported. The most important are:" | Numbers: start of a sentence. No semicolons |
| The three-item list | Parallel items, such as "A task is assigned," "A task is completed," "Someone comments." All three items kept. | Prose: parallel |
| "powerful, intuitive" | Deleted | Words table: marketing words |

### Must flag

| Item | Expected flag |
| --- | --- |
| "in near real time" | State the interval. Not replaced with a number. |
| "Notifications will soon support SMS delivery." | Unreleased feature. Remove or move to release notes. Not deleted by the agent. |
| "polls the events table every 500 ms and batches messages in the worker pool" | Internal implementation detail. Not deleted by the agent. |
| "the system may not always behave as expected" | Failure with no remedy. What fails, what does the reader see, what should they do. |
| "always ensures that you never miss an update" | Outcome promise. Suggest a plain statement of what the product does. |
| "SLA" | Acronym with no expansion in the source. Not expanded by the agent. |
| `acme_live_8f3a9c2e7b1d44e0` | Looks like a real credential. Suggest a placeholder such as `<your-api-key>`. Not edited. |

### Must not change

- `POST /notifications/subscribe` and the key string itself
- "500 ms," "15" as a count, and every other number
- "Free plan" and "Admin" as names
- The exact text of the checkbox label
- "notifications are not available on the Free plan" stays negative

## ui-sample.json (UI text mode)

The report's first line should name UI text mode and give the reason (a JSON string table). No key is changed. `{count}` is untouched.

### Must change

| Key | Accepted forms | Rule |
| --- | --- | --- |
| `dialog.delete_project.title` | "Delete this project?" The object comes from the key. | Dialogs: the title names the object |
| `dialog.delete_project.body` | "This can't be undone." or "You can't undo this." No exclamation point. | UI: no exclamation points |
| `dialog.delete_project.confirm` | "Delete" | Dialogs: the primary button names the action |
| `dialog.delete_project.cancel` | "Cancel" | Dialogs: the secondary is Cancel |
| `error.upload_generic` | "Something went wrong. Try again later." No _oops,_ no _please._ Also flagged, see below. | Error messages |
| `field.project_name.label` | "Project name" | Form fields: sentence case, no colon |
| `field.phone.label` | "Phone number *" at minimum. The asterisk is flagged, see below. | UI: sentence case |
| `toast.saved` | "Changes saved." | Toasts |
| `toast.deleted` | "Project deleted." with Undo as the one action. The second action is flagged, see below. | Toasts: one action |
| `tooltip.export` | "Export the current view as CSV" or "Export the current view as a CSV file." No "click this button," no trailing period on a phrase. | Tooltips. Interaction verbs |
| `menu.log_in` | "Log in" at minimum. Either changed to "Sign in" or flagged as a product-wide label decision. Both pass. | Words table and its Limit |

### Must flag

| Key | Expected flag |
| --- | --- |
| `button.submit` | Name the action. The agent can't tell what Submit does, so it asks rather than guessing. A change to a verb that the key supports also passes. |
| `button.new_project` | Either changed to "Create project" (the key names the object) or flagged. Both pass. "New" alone is a miss. |
| `error.upload_generic` | "Something went wrong" is the last resort. Ask for one message per known cause. |
| `error.file_too_large` | State the limit and what to do. Not supplied by the agent. |
| `field.project_name.placeholder` | The placeholder is the only instruction. Suggest an example value, without inventing one in the string. |
| `field.phone.label` | Required-field marking: which kind of field is rarer on this form, and is there a legend for the asterisk. |
| `toast.deleted` | Two actions in a toast. Keep Undo, move "view all projects" elsewhere. |
| `empty.projects` | "No items." is left as written. The skill can't tell whether this is a first-use state ("No projects yet") or a no-results state ("No projects match this filter"), and the two need different strings. It also has no next action. Ask which state this is and what the reader should do. Changing it to "No projects yet." counts as supplying a fact. |
| `link.learn_more` | Name the destination. |
| `banner.ai_summary` | "understands" (products don't think) and "always … perfect" (outcome promise). Suggest verbs such as _summarizes_ or _drafts._ The claim itself is not rewritten. |

### Must not change

- Every key
- `status.selected_count`, including the `{count}` token
- `badge.beta`
