---
name: oss-writing-style
description: Apply a plain, consistent writing style to software product UI text and documentation as a final standardization pass. It changes wording, formatting, and structure, never the facts, and flags anything that needs a human decision. Use when editing, reviewing, or drafting from a spec any customer-facing text, either documentation (feature docs, deployment guides, release notes, API docs, knowledge base) or UI text (labels, buttons, menus, dialogs, error messages, tooltips, toasts, empty states, microcopy, UX copy, string tables, resx, i18n files). Don't use it to edit code, legal text, or translations.
metadata:
  version: "1.0.0"
---

# OSS Writing Style

The voice is clear, direct, warm, and honest. Write like a person talking, lead with the point, and say what the reader should do next. This skill turns that into rules you can apply and check.

This skill is authoritative.

File paths in this skill are relative to this folder. The rules use US English spelling.

## Workflow

1. Detect the mode (next section). Read `references/ui-text.md` for UI text or `references/documentation.md` for documentation.
2. Review in the order under "Reviewing a draft": claims, terminology, machine tells, structure, proofreading. Open the other references when a check points to them.
3. Make the edits the fidelity contract allows. Turn everything else into a flag.
4. Run the fidelity check. Fix what it catches before you report.
5. Report in the format under "How to report."

## What you may change, and what you may not

This is the last pass over content that is already decided. Your job is presentation.

**You may change** punctuation, capitalization, spelling, word order, sentence breaks, list and table structure, how UI labels are formatted, terminology to the canonical forms in `references/terminology.md`, and word choice where the meaning stays identical.

**You may not change** any fact, number, date, version, name, step, sequence, condition, scope, or claim. Don't add information the source doesn't contain. Don't delete a statement because it looks wrong or out of date.

**Don't touch** code font or code blocks, commands, file paths, URLs, quoted error text, identifiers, version strings, string-table keys, placeholder tokens, or legal text.

**Use only** the source material and this skill. No web lookups, no filling gaps from memory. When a rule needs information the source doesn't have, flag it. Don't invent it.

**If the text already follows the rules, leave it.**

## Detect the mode

If the request names a mode, either `ui` or `docs`, use it. Otherwise decide from the input.

**UI text** when the input is a string table, a resx or i18n file, JSON or YAML of key-value strings, a spreadsheet of labels, a list of fragments without full sentences, or a request that names labels, buttons, dialogs, errors, tooltips, toasts, or microcopy.

**Documentation** when the input is prose: Markdown or a word-processor document with headings and paragraphs, a procedure, release notes, an API reference.

**Mixed** input follows its container. A document that quotes labels is documentation, and the quoted labels get documentation formatting. A string table that holds a long help paragraph is UI text.

If you can't tell and the request names no mode, ask before editing. Once you know the mode, read its reference file before you start.

## How to report

Start with one line naming the mode and what decided it. Then give the revised text, the changes, and the flags.

**Where the revised text goes.** If the input was a file, edit the file in place and don't paste the whole file back. If the file isn't under version control, write the revision to a new file next to it instead of overwriting the original. If the input was pasted into the request, return the revised text first.

**Template**

```
Mode: Documentation (Markdown file with headings and procedures)

Changes
- Capitalization: sentence-cased 14 headings
- Punctuation: replaced 3 em dashes, split 2 sentences at semicolons
- Terminology: "the user" to "you" in 6 places

Flags for the author
1. Line 42, "Updates in near real time": state the refresh interval. (prose.md, Flag vague claims)
2. Line 58, "will soon support SMS": unreleased feature. Remove, or move to release notes. (documentation.md, Claims)
```

**Keep the report honest and short.** One flag per distinct issue, with every location listed under it. Don't flag text that follows the rules, and don't list a change you didn't make. If nothing needs to change, say so in one line. Across several files, decide each terminology question once and apply it to all of them.

Examples in this skill and its references show each rule as a before and an after. They illustrate the rule. They are not phrases to find and replace.

## Step 1: What differs by mode

Most rules are shared. These differ.

| | UI text | Documentation |
| --- | --- | --- |
| **Naming a UI label in a sentence** | Match the UI exactly. No bold. | **Bold** the label, copied exactly from the source |
| **First person** | _My_ in a label that separates your content from shared content | Never |
| **Length** | The shortest version that still works | Complete, then tight |
| **Numbers 0 through 9** | Numerals | Words, unless space is tight |
| **Percent** | % | _percent_ in prose, % in tables and charts |
| **Trademark symbols** | None in functional UI. Attribution on the legal screen. Heading only on marketing surfaces. | First mention in the body, per the brand table |
| **Periods** | None on labels, titles, tooltips. Yes on full sentences. | Every sentence |

## When rules conflict

1. A fact in the source is never changed to satisfy a rule.
2. An existing UI label is copied exactly, even if it breaks a rule.
3. Where the skill is silent, flag it. Don't guess.

## Step 2: The checklist

### Say it straight (`references/prose.md`)

- Lead with the point.
- Start most sentences with a verb. Cut _you can_ when the sentence works without it.
- Active voice when the actor is named or obvious. Don't invent an actor.
- Present tense for how the product behaves. A statement about the future stays future. Flag it under Claims.
- Positive form when it means exactly the same thing. "Does not include" can become "excludes." A prohibition or a scope exclusion stays negative.
- Vague claims ("near real time," "key metrics") are missing facts. Flag them. Don't supply a number.
- Cut filler words and marketing adjectives (list in `references/terminology.md`). Keep a qualifier that states real behavior, such as _may_ or _up to._
- Cut a sentence that only announces the next one, if it carries no fact of its own.

### Address the reader

- Write to _you,_ the person who uses the product and changes its settings. Never _the user._ Same in UI and documentation.
- Everyone else gets a role name: _the admin, the customer, the reviewer._
- _User_ stays as a category word (_user permissions_) and in developer docs.
- Don't write _we_ unless the company has to be the speaker, as in a privacy notice.
- No gendered pronouns for a generic person. Rewrite to _you,_ a plural, or a role.

### Capitalize

- Sentence case for every heading, title, label, button, and menu item. Capitalize the first word, proper nouns, and the first word after a colon.
- When you name an existing label in documentation, copy its capitalization from the source.
- Title case only for product names, titles of works, and job titles. If you can't tell whether a word is a name, leave its case and flag it.
- No all caps for emphasis. Badges (PREVIEW, BETA) are the one exception in UI.
- A defined term keeps the capitalization its definition gave it. Only terms the document itself defines count.

### Punctuate (`references/mechanics.md`)

- No em dashes. No semicolons. See Step 3.
- Serial comma in a list of three or more.
- A colon only to introduce a list, not to attach an explanation to a sentence.
- Straight quotation marks. Exclamation points: no.

### Name things (`references/terminology.md`)

- Canonical product names from the product table. Replace only the aliases listed. Don't guess at others. If the table holds only the placeholder row, skip this check.
- One generic term for a generic capability, used consistently. If a bare word might mean either the product or the category, flag it instead of choosing.
- Third-party brands: exact casing per the brand table. Symbols by surface, per the mode table.
- Expand an acronym only if the expansion appears in the source. Otherwise flag.

### Claims (`references/documentation.md`)

Flags, not edits. You can't verify what has shipped.

- Flag a sentence that describes a planned, upcoming, or unreleased feature.
- Flag internal mechanics: service names, table names, polling intervals, call sequences.
- Flag a failure described with no remedy for the reader.
- Flag _always, never, guarantees, ensures, eliminates,_ or _perfect_ applied to an outcome or to model behavior, with a suggested plainer statement.
- Flag anything in a sample that looks like a real key, token, password, internal hostname, or customer record.

### Format (`references/documentation.md`, `references/ui-text.md`)

- Bullets for any dense list of states, limits, or options. Keep every item and its wording.
- Lists parallel in structure. Tables for data with two or more attributes.
- In UI, each component has its own rules. See `references/ui-text.md`.

## Step 3: Don't sound like a machine wrote it

**The em dash is the strongest tell. Don't use it.** Replace it by the job it was doing.

| The dash was doing this | Use this |
| --- | --- |
| Setting off a definition or aside | A pair of commas |
| Introducing a list | A colon |
| Adding an aside the sentence could drop | Parentheses |
| Explaining, or joining two related statements | A period, and two sentences |
| Marking an abrupt turn | Rewrite so the turn isn't needed |

Also cut these:

- **Semicolons.** Split the sentence or make a list.
- **A colon mid-sentence** that introduces an explanation instead of a list.
- **"It's not just X, it's Y."** Say what it is.
- **Openers that announce.** "In today's fast-paced digital world."
- **Sentences that introduce the next thing.** "The table below shows the supported connectors."
- **Stacked hedges.** "It's generally usually best to typically avoid." One hedge that states a real limit can stay.
- **Filler intensifiers.** _Genuinely, actually, literally, truly, really._
- **Moreover, Furthermore, Additionally** chaining paragraphs together.
- **A punchy one-liner after every rule.**
- **Bold scattered through prose** for emphasis.
- **A closing paragraph that restates the opening**, when it adds no fact.

## Gotchas

Mistakes this pass tends to make. Check for them before you report.

- **Filler words have real uses.** _Just_ meaning "only" or "a moment ago," _simply_ or _really_ inside a quotation or a product name. Cut a word from the delete list only when it's working as an intensifier.
- **A term swap can rename a product.** If the strings already say _Log in_ everywhere, changing one to _Sign in_ is a product decision. Flag it. Apply the Words table freely to prose.
- **Don't fill a gap.** No invented remedy for an error, interval for "near real time," example for an empty placeholder, or definition for an undefined status. Flag, with a suggestion if you have one.
- **Code is never edited,** even to fix a typo inside it. Flag the typo.
- **Clear text that breaks no rule stays as written,** even when you'd phrase it differently. Rewriting to taste is the most common complaint about automated style passes.
- **Labels are facts.** In documentation, a label is copied from the source even if its capitalization breaks a rule. You can't see the screen.

## References

| File | Load when |
| --- | --- |
| `references/ui-text.md` | UI mode. Every component from buttons to toasts, brands in UI, localization |
| `references/documentation.md` | Documentation mode. Labels, formatting, headings, procedures, lists, tables, release notes, API reference, code samples, claims flags |
| `references/prose.md` | You're rewording a sentence rather than fixing punctuation, or the text is for global readers |
| `references/terminology.md` | A product name, brand, acronym, or word-choice question comes up |
| `references/mechanics.md` | Numbers, dates, dashes, and punctuation questions, and the proofreading sweep in every review |
| `references/inclusive-language.md` | The text refers to people, or describes an AI feature |

## Reviewing a draft

Work in this order.

1. **Claims.** Flag anything unshipped, internal, unremedied, or overpromised.
2. **Terminology.** Product names, brand casing and symbols, defined terms, _the user,_ a bare word that could mean the product or the category.
3. **Machine tells.** Em dashes and semicolons first, then the rest of Step 3.
4. **Structure.** Heading case, bullets for dense lists, parallel lists, sentences that only announce. In UI mode, each string against its component rules.
5. **Proofread.** The sweep at the end of `references/mechanics.md`.
6. **Fidelity check.** Compare before and after. Every number, name, date, version, step, condition, key, and token is unchanged. Nothing added. Nothing deleted that carried a fact.

Where a rule is ambiguous, flag it.
