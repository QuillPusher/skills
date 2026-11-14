[![](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# OSS Writing Style skill

An agent skill that applies a plain, consistent writing style to software product UI text and documentation as a final standardization pass. It changes how text is worded, formatted, and structured. It never changes the facts, and it flags anything that needs a human decision.

These rules are a compact, checkable form for an AI agent, based on the same plain, consistent writing style. The skill is self-contained: everything the agent needs is in this folder.

## What's here

| File | Words | Contents |
| --- | --- | --- |
| `SKILL.md` | ~2,200 | Workflow, fidelity contract, mode detection, report template, mode table, precedence, the checklist, machine tells, gotchas, when to load each reference, review order |
| `references/ui-text.md` | ~1,800 | Every UI component: buttons, dialogs, errors, forms, tooltips, toasts, empty states, links, accessibility, brands in UI, localization |
| `references/documentation.md` | ~1,850 | Bold for labels, formatting conventions, headings, fluff, procedures, lists, tables, callouts, links and images, release notes, API reference, code samples, claims flags |
| `references/prose.md` | ~1,200 | Sentence-level rules, each with its fidelity limit, plus global readers |
| `references/terminology.md` | ~1,400 | Product-name template, third-party brand table, defined terms, acronyms, the Words table and its limits |
| `references/mechanics.md` | ~1,050 | Numbers, dashes, punctuation, proofreading sweep |
| `references/inclusive-language.md` | ~600 | Pronouns, gender-neutral words, biased terms, combat metaphors, disability, products aren't people |
| `tests/` | n/a | Manual test cases: a documentation sample, a UI sample, and the expected results |

`SKILL.md` loads every time. The references load when the work calls for them. The table at the end of `SKILL.md` says when.

## Before you use it

Two tables in `references/terminology.md` are templates:

- **Canonical product names.** Holds a placeholder row. Add your product names and the aliases to retire. Until you do, the skill skips the product-name check.
- **Third-party brands.** Holds example rows marked Confirm, which makes the skill flag them rather than add symbols. Replace them with the brands your content names, and set each symbol only after checking the owner's trademark guidelines.

Keep company-specific rows in your own copy or fork. The shared version stays generic.

## Installing it

The skill follows the [Agent Skills](https://agentskills.io) format: a folder with a `SKILL.md` that has `name` and `description` frontmatter, plus a `references` folder the agent reads when it needs to. Any harness that supports that format can load it. The folder name must match the `name` field (`oss-writing-style`). If you rename one, rename the other.

- **Harnesses with skill support.** Copy or symlink this folder into the harness's skills directory. For Claude Code, that's `~/.claude/skills/` for every project or `.claude/skills/` inside one repository. For other harnesses, see their documentation for the skills location.
- **Harnesses without skill support.** Put the contents of `SKILL.md`, without the frontmatter, in the harness's project instructions file or system prompt. Make the `references` folder readable to the agent, and keep the paths relative to that folder.

A symlink keeps the installed copy in sync with your edits. If you copy instead, copy again after each change.

## Using it

Commit the text or save a copy before you run the skill, so you can diff the result. Then give the agent the text to review or edit, as a file or pasted into the request, and ask it to apply the writing style.

**Choosing a mode.** The skill detects UI text or documentation from the input and states its decision in the first line of the report. To remove the guess, name the mode in the request, such as `ui` or `docs`, or say "UI strings" or "documentation." In Claude Code, `/oss-writing-style ui` and `/oss-writing-style docs` work.

**What you get back.**

1. The revised text. For a file, the agent edits the file in place (or writes a copy next to it when the file isn't under version control) and doesn't paste the whole file into the chat.
2. A list of changes, grouped by type.
3. Flags for the author: anything the skill couldn't fix without a fact it doesn't have, such as a missing interval, an unreleased feature, or an error message with no next step.

Review the flags yourself. The skill never resolves them on its own.

## Testing it

The `tests` folder holds manual test cases: a documentation sample, a UI sample, and the expected results. Run them in your target harness before you rely on the skill, and again after any change to a rule.

**If you are an agent and the request is to test this skill, run these steps.**

1. Copy the sample named in the request to a scratch folder outside this repository. Never edit the copy in `tests/`. It is the fixture.
2. Read `tests/expected-results.md` for that sample before you edit anything.
3. Apply this skill to the copy in the mode in the table below.
4. Compare your output with `tests/expected-results.md`, item by item.
5. Report pass or fail for each item. For a miss, say what you did instead.

| File | Mode | What it checks |
| --- | --- | --- |
| `tests/docs-sample.md` | Documentation | Headings, fluff, machine tells, procedures, lists, claims flags, code and credentials |
| `tests/ui-sample.json` | UI text | Buttons, dialogs, errors, form fields, toasts, empty states, tooltips, links, tokens, badges |
| `tests/expected-results.md` | Both | What must change, what must be flagged, and what must stay as it is |

**If you are a person testing the skill,** give the agent the sample path and the mode. In Claude Code, use `/oss-writing-style docs` for the document or `/oss-writing-style ui` for the strings. In other harnesses, ask for the writing style pass and name the mode. Then check the agent's report against the pass criteria.

**Pass criteria**

- Every **Must change** item is changed to an accepted form.
- Every **Must flag** item appears in the flags.
- Nothing under **Must not change** is altered.
- No fact was added. No invented limit, interval, action, example value, or definition.

A **Must change** item that was flagged instead of changed is a miss. A **Must flag** item that was changed instead of flagged is a worse miss, because the agent supplied a fact.

The full pass criteria and the issue template are in [`tests/README.md`](tests/README.md).

## Changing it

Every rule should be checkable. If you can't tell whether a draft passes, rewrite the rule.

Every rule that could change meaning carries a **Limit** line saying where to stop and flag. If you add a rule, add its limit.

Keep `SKILL.md` under about 2,500 words and 300 lines. The Agent Skills guidance is under 500 lines and 5,000 tokens, and every line there is a tax on every task. The fidelity contract, mode detection, and gotchas are the sections that earn their length.

Each rule has one owner file. `SKILL.md` summarizes and points. Rule files state rules and don't cite sources. Reasoning lives here.

Keep everything tool-neutral and platform-neutral. Use relative paths and forward slashes. Don't rely on features only one harness has, such as argument substitution.

When you change a rule here, update or add a case in `tests/` in the same change.

## The operating model

The agent running this skill works from the source document and this skill, nothing else. No web lookups, no filling gaps from memory. It edits presentation and produces a report with three parts: the revised text, a grouped list of changes, and a list of flags for the author. Anything that would add, remove, or alter a fact becomes a flag with a suggestion, not an edit. A document that already follows the rules comes back unchanged.

This means some common review requests (remove unreleased features, remove internal details, soften AI promises) are implemented as flags. The agent can't know what has shipped or what's internal. The author can, and decides.

## Decisions and their reasons

Each of these could have gone the other way. Recorded so a contributor can disagree with the reasoning instead of guessing at it.

**Presentation only, facts flagged.** The skill is the last step on a finished document. A rule like "be specific: write 'refreshes every 15 seconds,' not 'near real time'" invites an agent to invent the number. Every such rule is framed instead as: flag the vague phrase, name what's missing, rewrite only if the specific value appears elsewhere in the source. The same limit applies to positive-form rewrites (a prohibition or scope exclusion stays negative), active-voice conversion (don't invent an actor), tense (don't move a future statement to the present), fluff cutting (a sentence with a scope word carries a fact), and list reformatting (keep every item as written).

**Examples are labeled as examples.** Every table of examples is headed Before and After, and every reference file opens with one line saying the tables illustrate a rule and are not phrases to find and replace. An agent pattern-matching "does not include" to "excludes" everywhere would break sentences where the negative is the fact.

**A gotchas section in `SKILL.md`.** The mistakes an automated style pass makes most often are not rule violations but over-application: deleting _just_ when it means "only," renaming a label the product uses everywhere, inventing a remedy for an error message, and rewriting clear text to taste. Those are listed in `SKILL.md` where the agent reads them on every run, rather than in a reference file it might not open.

**A report template, not a description of the report.** Agents follow a concrete structure more reliably than prose that describes one. The template also fixes two habits that waste reviewers' time: pasting a whole file back into the chat, and listing the same flag once per occurrence.

**Sentence case for all headings.** Title case was considered. Sentence case is the norm in current software style guides, it's easier to apply consistently, and it reads as less formal.

**Bold for UI labels in documentation, nothing in UI text.** Bold survives conversion between Markdown and word-processor formats in both directions, and it doesn't collide with italic, which this style uses for new terms. Bold crowds a page too, so the rule pairs with two limits: describe the action instead of naming the control where you can, and turn any paragraph with more than two or three bold labels into a procedure. Labels are copied with the source's exact capitalization because the agent can't see the screen.

**Write to _you,_ never _the user._** One reader: the person who uses the product day to day and changes its settings. _You_ holds for UI and documentation alike. _User_ survives as a category word (_user permissions_) and in developer docs for the end user of the reader's software.

**One skill, two modes, detected and stated.** UI text and documentation share about 80 percent of their rules (fidelity contract, voice, terminology, punctuation, machine tells). Two skills would duplicate that and drift. The skill detects the mode from the input shape. A string table, resx, i18n file, label spreadsheet, or a set of fragments means UI. Prose means documentation. Mixed input follows its container. It states the decision in the first line of its report, accepts a mode named in the request to skip the guess, and asks when it can't tell.

**UI rules organized by component.** Published design systems and content guidelines agree on component-level rules: dialog titles as questions with action-named buttons, one error per cause, labels carry the instruction and placeholders never do, one-action toasts with Undo, tooltips as phrases, link text naming the destination, text labels on icon-only controls, no hard-coded locale formats, badges as the one all-caps exception, and no _please_ or _sorry._ Organizing by component lets an agent check each string against the rules for what it is.

**Mark the rarer kind of form field.** Usability research disagrees on asterisks versus "(optional)," and the disagreement turns on the form: when most fields are required, marking the few optional ones is less clutter, and when most are optional, the asterisk is the convention readers already know. The rule follows the form rather than picking a side, and the skill flags the question when it can't tell which kind is rarer.

**One generic term for an AI feature, rather than a mandated one.** Teams disagree about _assistant, AI assistant,_ and _virtual assistant,_ and a shared guide shouldn't settle a naming debate. What a style pass can check is consistency, and the one real hazard, _agent,_ which can mean a person or a program.

**No trademark symbols in functional UI.** The question "which occurrence on a screen is first" has no good answer, and trademark guidance generally says not to mark every occurrence and, for globally distributed material, to prefer an attribution notice over inline symbols. The rule is by surface, which removes the judgment: functional UI takes no symbol, the legal or About screen carries the attribution line, and a marketing surface inside the product takes one symbol on its heading. Source strings that already carry symbols are kept and flagged.

**Trademark symbol at first mention in the body, plus an attribution line.** Legal and editorial convention puts the symbol on the first or most prominent mention per document, not per section. Technical documentation commonly relies on a closing attribution notice instead. The skill does both: a first-mention symbol where the brand table confirms it, plus a generic attribution line flagged for legal review. The brand table ships with every entry marked Confirm, which makes the agent flag rather than guess.

**Composition principles, not grammar rulings.** `references/prose.md` keeps the classic composition principles that current style guides still agree with (cut needless words, positive form, parallel structure, modifiers next to what they modify) and leaves out grammar rulings that linguists have since discredited (generic _he,_ the ban on singular _they_). "Use specific, concrete language" is kept as a principle but inverted for an agent: flag vagueness, don't manufacture precision.

**No em dashes, no semicolons.** Readers now treat the em dash as a marker of machine-generated text, and semicolons rarely appear in everyday writing. The em dash ships with a replacement table so the ban doesn't just remove an option. Both are house choices, so a fork that keeps em dashes only has to change one rule.

**Literal values keep punctuation outside quotation marks.** Periods and commas go inside a closing quotation mark, except after a literal value such as a search term. Writing `No projects match "sales."` would suggest the period is part of the search term.

**"Groups of three" dropped as a machine tell.** An agent could read it as license to cut a real third item. Any tell that could be satisfied by deleting information is out.

**Words table choices.** _Enable_ isn't swapped for a plainer word because it means "turn on" in software. _Press_ stays for keys. Hedges (_may, up to, typically_) are "keep or flag," not "delete," because they usually state real behavior. Latin abbreviations are replaced because readers and translation tools misread them. The delete rows carry a limit, because _just_ and _simply_ have meanings that aren't filler.

**Length.** What stays in the skill is what shows up in most reviews: heading case, terminology consistency, UI label formatting, procedures, dense lists, fluff, claims, and the machine tells.

**Generic examples, not real product names.** Examples use a fictional project-and-task app (projects, tasks, team members, a reporting console, a sync connector) so they stay correct as products change and carry no company's internal vocabulary. Product names in examples are fictional. Third-party brand names in the brand table are real because standardizing their casing is the point.

**Tool-neutral.** The skill uses only the `name`, `description`, and `metadata` frontmatter fields and relative paths, so it loads in any harness that supports the Agent Skills format. The mode is read from the request text rather than from harness-specific argument substitution.

## Known gaps

- The brand table ships with example rows only. Each needs verification before its symbol column is filled in.
- The tests are manual only. A person runs the sample through an agent and compares the output, and there is no automated harness.
- No linter ruleset. The mechanical rules (serial comma, Latin abbreviations, em dashes, title case, _click_) could be expressed for a prose linter so they're caught before the agent pass, leaving the agent the judgment calls.
- No worked before-and-after file with full paragraph rewrites.
- The Words table should grow from real review findings.
