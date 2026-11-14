# UI text

Words inside the product: labels, buttons, menus, dialogs, form fields, tooltips, toasts, errors, empty states, notifications. UI text is read by someone in the middle of doing something else, so every extra word costs them.

Tables show each rule as a before and an after. They illustrate the rule. They are not phrases to find and replace.

**Limit.** UI strings often live in a string table with keys, placeholder tokens like `{name}`, and character limits you can't see. Never change a key, a token, or anything in code font. If a string looks truncated to fit a limit, flag it rather than lengthening it.

## Quick check for any string

1. Does it say what happens, or what the reader should do?
2. Sentence case?
3. No period on a label or title. A period on a full sentence.
4. Is it the shortest version that still works?
5. No _please, sorry,_ or _oops._

## Capitalization and punctuation

- Sentence case for every label, title, menu item, button, and message. Capitalize the first word and proper nouns.
- Generic UI element names are lowercase in running text: _toolbar, menu, tab, dialog._
- All caps only for a badge: PREVIEW, BETA, NEW.
- No period, colon, or ellipsis at the end of a label, title, menu item, or button.
- A period on any full sentence, even a two-word one. Tooltips and field descriptions take no period unless they run to two sentences.
- A progress message can end with an ellipsis: "Syncing…"
- No exclamation points.

## Buttons

- Lead with the verb that names the action. One word where possible, three at most. Four or more means it should be a link.
- Say what happens, not what the control is.
- _Create_ makes something new. _Add_ brings in something that exists. _Install_ is for software.
- Name the action instead of answering a question. _Yes_ and _No_ are acceptable only when the title is a yes-or-no question and no verb fits. Never _OK_ to confirm an action.

| Before | After |
| --- | --- |
| Submit | Save changes |
| New | Add a project |
| OK | Delete |
| Click here to continue | Continue |

## Dialogs and confirmations

- The title is a question or a statement that names the object: "Delete this project?" Never "Are you sure?" or "Warning!"
- The body states the consequence in one or two sentences: "Its tasks move to your default project."
- Two actions at most. The primary button names the action (Delete, Remove, Discard). The secondary is Cancel. Never OK. Yes and No only when the title is a yes-or-no question and no verb fits.
- A destructive primary button repeats the verb in the title.

| Before | After |
| --- | --- |
| Are you sure? [Yes] [No] | Delete this project? Its tasks move to your default project. [Delete] [Cancel] |

## Error messages

Say what happened, why if the reader can act on the cause, and what to do. Don't blame the reader.

- One message per known cause. "Something went wrong" is the last resort, not the default.
- An error reports a problem that already happened. A warning is about a problem that might. Don't dress an error as a warning.
- No _please, sorry, oops,_ or _unfortunately._
- Passive voice is fine when it keeps blame off the reader ("The password wasn't recognized").

| Before | After |
| --- | --- |
| Oops! We couldn't save your file. | The file didn't save because the disk is full. Free up space and try again. |
| Invalid date | Enter the date as YYYY-MM-DD, for example 2026-03-14. |
| An unexpected error occurred. | The connector lost its link to the sync API. Check network access to the endpoint. |

**Limit.** If the source says what happened but not what to do, and nothing in the source tells you the cause or the remedy, don't invent one. Flag it: "Error text has no next step."

## Form fields

- The label carries the one instruction the reader needs. A noun or a short noun phrase, sentence case, no colon: "Project name."
- Placeholder text is supplementary. It disappears when the reader types, so it can never be the only instruction. Use it for an example of the expected input.
- Help text below the field explains a format or a rule the reader can't guess: "Use 8 or more characters." Add it only when getting the input wrong would cause an error.
- Mark whichever kind of field is rarer. If most fields are required, end each optional label with "(optional)." If most are optional, mark the required ones with an asterisk and explain it once at the top of the form. If you can't tell which kind is rarer, flag it.

| Before | After |
| --- | --- |
| Label: none. Placeholder: Enter the project name here | Label: Project name. Placeholder: Website redesign, Q3 launch |
| Label: Email address * (on a form where every field is required) | Label: Email address |
| Label: Phone number. Placeholder: Phone number | Label: Phone number (optional) |

## Tooltips

A tooltip names or briefly describes the control it's attached to. A phrase, not a paragraph. No period unless it runs to two sentences. Don't put anything essential in a tooltip, because keyboard and touch users may never see it.

> Filter by project
>
> Export the current view as CSV

## Toasts and notifications

- One line. It confirms something that already happened or reports something that needs attention.
- One action at most, and Undo is the best one. No links inside the text.
- If it needs two actions, or the reader must deal with it before continuing, it's a dialog, not a toast.

| Before | After |
| --- | --- |
| Your changes have been successfully saved to the system! | Changes saved. |
| The project was deleted. Click here to undo or here to view projects. | Project deleted. [Undo] |

## Success messages

Name what happened. Past tense, one line, no exclamation point.

> Project saved.
>
> Report sent to 3 recipients.

## Empty states

An empty state says why there's nothing here, then what to do. A first-use state ("No projects yet") and a no-results state ("No projects match this filter") are different and shouldn't share a string.

| Before | After |
| --- | --- |
| No items. | No projects yet. Add a project to start tracking work. |
| Nothing found. | No projects match "sales". Clear the filter or try another name. |

**Limit.** If the source empty state has no next action and you don't know what the action is, flag it.

## Links

Link text names the destination or the result. Never "click here," and never "learn more" on its own.

| Before | After |
| --- | --- |
| Click here to view the sharing rules. | View the sharing rules. |
| Learn more | Learn more about recommendations |

## Accessibility text

- Every icon-only control needs a text label a screen reader can read. Name the action: "Close," "Filter," "Refresh."
- Alt text for an informative image states what it shows or does, not that it's an image. A decorative image gets empty alt text.
- Don't refer to color alone. "The red status" means nothing to a screen reader. Name the state.
- Don't refer to position. "The button on the left" or "see below" breaks when the layout changes or a screen reader reads the page in order. Name the control, or link to the section.

## Text the product generated

When the product did something on its own, use past tense so the reader knows it already happened, and make clear that a judgment was applied and may need review.

> A summary was drafted from the last 20 comments. Review it before you share it.

Flag _always, never,_ and _guarantees_ in this kind of text. Don't claim certainty the model doesn't have.

## Interaction verbs

These describe the action without assuming a mouse, a finger, or a keyboard.

| Verb | Use for |
| --- | --- |
| **Open** | Apps, menus, files |
| **Close** | Apps, panes, dialogs, windows, files |
| **Go to** | A place in the UI (a tab, a page, a menu) |
| **Select** | Options, values, links, menu items, buttons |
| **Clear** | Unchecking a checkbox |
| **Enter** | Typing a value |
| **Press** | A key or key combination (press Enter, press Ctrl+S) |
| **Turn on, turn off** | A toggle or a setting |

Avoid _click_ and _tap._ Each assumes one input device.

| Element | Preposition |
| --- | --- |
| dialog, pane, list, box, window | in |
| tab, page, menu, toolbar | on |

## Naming a label inside a UI sentence

Match the label exactly and let its capitalization mark it. Don't bold. Use quotation marks only when the label would otherwise be unreadable in the sentence.

> Select Save changes to keep your edits.
>
> Move the task to the "Needs review" column.

## First person

_You_ is the default. _Me_ and _my_ are fine in a label where the reader is the speaker: "Keep me signed in," "Email me when someone mentions me." Use _My tasks_ only when there is also a shared view to tell it apart from. Don't mix _my_ and _your_ on one screen. If the source does, flag it.

## Third-party brands in UI

Use the exact casing from the brand table in `terminology.md`. Whether a symbol appears depends on the surface, not on which occurrence comes first.

| Surface | Rule |
| --- | --- |
| **Functional UI**: labels, menus, settings, status, errors, tooltips, connector names | No symbol. Correct casing only. |
| **Legal, About, or Third-party notices screen** | The attribution line: "All product and company names are trademarks or registered trademarks of their respective owners." Symbols only where the owner's guidelines require them. |
| **Marketing surfaces inside the product**: onboarding screen, integration catalog tile, a "Connect to X" landing page | One symbol, on the screen's title or heading, per the brand table. Not in body text or buttons. |

There is no "first occurrence" judgment to make. Either the surface takes no symbol, or the symbol goes on the heading.

**Limit.** If the source strings already carry symbols, keep them and flag for a decision. Don't strip or add on your own.

## Localization

- Keep strings short. Translations run 30 to 40 percent longer than English.
- Don't build a sentence from fragments joined at runtime. Word order changes across languages.
- Don't hard-code a date, time, or number format into a string. The platform supplies the locale.
- Placeholder tokens such as `{count}` or `%s` stay exactly as written.
