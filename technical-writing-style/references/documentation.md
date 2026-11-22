# Documentation

Prose about the product: feature documents, deployment guides, runbooks, release notes, API references, knowledge base articles. Documentation is read by someone who is stuck or about to make a decision. Accuracy comes first, brevity second.

Tables show each rule as a before and an after. They illustrate the rule. They are not phrases to find and replace.

## UI labels in documentation

Bold the label, and copy it exactly as the screen shows it, capitalization included.

> Select **Export**.
>
> On the **Sharing** tab, select **Invite people**.
>
> Clear the **Send email notifications** checkbox.

- Bold is for UI labels and run-in headings only. Never for emphasis.
- Prefer describing the action to naming the control. "Save a copy of the report" needs no bold.
- Don't name the control type unless it prevents confusion.
- If the source writes **Export As**, keep **Export As**, even though a new label would get sentence case. You can't see the screen, so the source's rendering of a label is the fact.
- Drop a label's trailing colon or ellipsis.
- A paragraph with more than two or three bold labels should be a numbered procedure.

## Formatting conventions

| Element | Format | Example |
| --- | --- | --- |
| **UI labels** | Bold, exact capitalization | Select **Export**. |
| **Menu paths** | Bold labels joined by a spaced greater-than sign, not bold | Select **Settings** > **Members** > **Invite**. |
| **Commands, code, file names, paths, parameters, terminal input** | Code style. Don't edit what's inside. | Run `git status`. |
| **Placeholders in code** | Descriptive name in angle brackets | `sync --project <project-id>` |
| **Keys and shortcuts** | Key names as printed, plus sign with no spaces. Each platform's version when they differ. | Press Ctrl+S (Windows and Linux) or Cmd+S (macOS). |
| **A new term being defined** | Italic on first use | A _workspace_ holds a team's projects. |
| **Quoted error text** | Quotation marks, exact wording | If you see "Sync paused," check your connection. |
| **File formats** | Format in capitals, extension in code style | a CSV file, `.csv` |

**Limit.** If the source gives only one platform's shortcut or path, don't add the others. Flag it if the document is meant for several platforms.

## Headings

The shared heading rules are in `SKILL.md`. For documentation, also:

- One top-level heading per page, the title. Don't skip levels. Fix a skipped level by changing the heading level, not by adding a heading.
- Front-load the words a reader would scan for.
- A task heading starts with a verb ("Invite people"). A concept heading is a noun phrase ("Permissions").
- Keep headings at one level parallel.
- Don't stack two headings with no text between them. Flag it rather than inventing text.
- Don't introduce an acronym in a heading.
- Avoid ampersands and plus signs.
- No period at the end. A question mark is fine when the heading asks the reader's question.

## Cut the fluff

The most common review finding. Each of these adds length and no information.

| Cut this | Because |
| --- | --- |
| "The table below shows the supported connectors." | The table is right there |
| "This section explains how to configure notifications." | The heading already said so |
| "In today's fast-paced digital world ..." | Says nothing |
| "It is important to note that ..." | State the thing |
| A closing paragraph that restates the opening | The reader already read it |

**Limit.** Cut a sentence only if every fact in it appears in the heading or in the next sentence. "This section explains how to configure notifications for shared projects" carries a scope ("shared projects") that the heading may not. Move the fact, then cut.

## Procedures

- Number the steps.
- One action per step. Combine only short actions that happen in the same place. Never reorder steps.
- Start each step with a verb. If the reader needs to know where they are first, lead with the location: "On the **Sharing** tab, select **Invite people**."
- A condition goes before the action: "If you use single sign-on, select **Use SSO**."
- An optional step starts with "Optional:".
- Full sentences. Capital letter, ending period.
- Keep the step that finishes the job, such as selecting **Apply**. If the source has no finishing step, flag it. Don't add one.
- Prerequisites go before step 1. If the source has none, don't add any. Flag it if a step clearly depends on something unstated.
- A step that isn't an action ("Changes are saved automatically.") becomes a result sentence under the previous step or a note after the list. Keep every action and every fact.
- About seven steps. If the source has more, split the list at a natural pause and keep the order. Don't cut steps.
- A single-step procedure uses a bullet, not a number.
- Menu paths use a spaced greater-than sign, not bold: Select **Settings** > **Members** > **Invite**.
- Give the procedure a heading that says what it accomplishes. Skip an intro sentence that repeats the heading.

## Lists

- Two to seven items. If the source has more, don't cut items. Consider splitting into two lists under subheadings, or flag it.
- Parallel structure. All noun phrases, or all verb phrases.
- Introduce with a heading, a full sentence, or a fragment ending in a colon.
- Capital letter to start each item.
- Periods only when the items are full sentences or complete the lead-in sentence.
- No semicolons, commas, or conjunctions at the ends of items.

**Bullets for dense status lists.** A paragraph carrying several comma-separated conditions, limits, or states is unreadable. Break it out as a term list: bold term, period, definition. Keep every item and every definition as written.

| Before | After |
| --- | --- |
| A build can be pending, which means it's waiting for a runner, running, which means it's in progress, failed, or succeeded. | **A build has one of four statuses:**<br><br>- **Pending.** It's waiting for a runner.<br>- **Running.** It's in progress.<br>- **Failed.**<br>- **Succeeded.** |

In the after, _Failed_ and _Succeeded_ have no definitions because the source gave none. Don't write one.

## Tables

- Use for data with two or more attributes. For a plain list of similar things, use a list.
- Identify the row in the leftmost column.
- Sentence case in headers and cells, except code values and identifiers, which keep their case.
- Specific column headers. "Employee" or "Group," not "Name."
- Never leave a cell blank to mean "nothing here." Write _None_ or _Not applicable._ If you don't know which, flag it.
- Introduce a table with a full sentence ending in a period, not a colon.

## Notes and warnings

- **Note** is helpful but not required. **Important** is needed to succeed. **Warning** is a risk of data loss, a security exposure, or downtime.
- A warning says what happens and how to avoid it. If the source's warning doesn't, flag it.
- Don't stack two callouts, and don't put a step inside one.
- Don't change a callout's level on your own. If the level looks wrong, flag it.

## Links and images

- Link text names the destination. Not "click here."
- A cross-reference uses the exact title of the section or page. Flag one that names a section that doesn't exist.
- "Above" and "below" become a link to the section by name when the target is clear. Otherwise, flag.
- Alt text says what an informative image shows. Don't start with "Image of."
- Flag a step that depends on a screenshot to make sense, and any screenshot or example that seems to show real customer data.

## Release notes

- One entry per change the reader can notice. Group entries under fixed headings in this order: New, Changed, Fixed, Deprecated, Removed, Security. Skip empty headings.
- Each entry starts with what changed, from the reader's side, not with a ticket number or a team name. Moving a ticket number to the end of the entry is an edit. Deleting it isn't.
- If an entry says what the reader must do, keep the deadline and the version exactly as written.
- Flag an entry whose category you can't tell from its text. Don't guess.

## API reference

- HTTP methods in capitals, paths in code style: `GET /projects/{id}`.
- An endpoint description starts with a present-tense verb ("Returns the project").
- Parameter tables use the same column order throughout. Reordering columns is an edit. Adding a type, a default, or a required flag the source doesn't give is not. Flag the gap.
- One name for one thing. If the prose and the field name disagree (_project key_ and `project_id`), flag it. You can't tell which is right.

## Code samples

- Never edit code, commands, or sample values, even to fix a typo. Flag the typo.
- Flag anything that looks like a real key, token, password, internal hostname, or customer record, and suggest a placeholder such as `<your-api-key>` or `example.com`.
- Flag a sample with no stated language or shell when the document mixes several.

## Claims

These four checks have consequences outside the document, so they run first in any review. They produce flags, not edits. You can't verify what has shipped, what's internal, or what's true. The author can.

### Flag unreleased features

A sentence that describes a planned, upcoming, or future capability, or one behind a setting the reader can't turn on.

| Text | Flag |
| --- | --- |
| The dashboard will soon report response time by team member. | Unreleased feature. Remove, or move to release notes. |

If a sentence uses present tense and you have no signal it's unreleased, leave it. You can't tell.

### Flag internal implementation details

Service names, table names, polling intervals, cache behavior, internal call sequences.

| Text | Flag |
| --- | --- |
| The sync service polls the cache every 400 ms and writes to the events table. | Internal detail. Suggest: "Changes sync every few seconds." |

Some intervals and names are customer-facing configuration. Flag, don't delete.

### Flag failures with no remedy

A sentence that says something can fail without saying what the reader will see or what to do.

| Text | Flag |
| --- | --- |
| The connector may not always work as expected. | What fails, what does the reader see, and what should they do? |

### Flag promised outcomes

_Always, never, guarantees, ensures, eliminates, perfect,_ or _the best,_ applied to an outcome or to model behavior.

| Text | Flag |
| --- | --- |
| Recommendations guarantee higher customer satisfaction. | Outcome promise. Suggest: "Recommendations rank the articles most likely to answer the question." |
| The AI always picks the best answer. | Outcome promise. Suggest: "The model ranks possible answers by how closely they match the question." |

The suggestion in a flag is a starting point for the author. Don't apply it yourself.
