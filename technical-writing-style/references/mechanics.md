# Mechanics

Numbers, dashes, punctuation, and the proofreading sweep. Look things up here as needed.

Tables show each rule as a before and an after. They illustrate the rule. They are not phrases to find and replace.

## Numbers

Copy a number that appears in the UI exactly as the UI shows it. Never reformat an identifier, a version string, or a code value. Otherwise:

| Situation | Write | Example |
| --- | --- | --- |
| **Prose, 0 through 9** | The word | five projects |
| **Prose, 10 and up** | Numeral | 12 members |
| **UI, tables, tight space** | Numeral, any size | 5 projects |
| **Several numbers of the same kind in one sentence** | Numerals throughout | The release has 14 fixes, 3 new features, and 2 known issues. |
| **Start of a sentence** | Never a numeral | Eleven projects are active. |
| **Measurements and durations** | Numeral, even below 10 | 3 seconds, 5 minutes, 0.75 GB, 80 × 80 pixels |
| **Time of day** | Numeral plus AM or PM, or 24-hour time if the product uses it | 10:45 AM, or 22:45. Write _noon_ and _midnight,_ not 12:00. |
| **Percent in prose** | Numeral plus _percent_ | 50 percent |
| **Percent in UI and tables** | Numeral plus % | Resolved: 87% |

**Commas** from four digits (1,024). None in years (2026), after a decimal point, or in version numbers, port numbers, and identifiers (port 8080).

**Units** A space between number and unit (25 MB, 30 ms), none before % (87%). Plural unit for anything that isn't exactly 1 (0.5 seconds, 1 second, 5 seconds).

**Dates** Spell out the month. 6/12/2026 means two different dates depending on the reader's country. Write _June 1,_ not _June 1st._ ISO form (2026-06-12) in data, logs, and code. If converting a numeric date would mean guessing the day and month order, flag it.

**Ranges** In prose, _from 5 through 50._ In tables and UI, an en dash with no spaces (2016–2026). For times, _to_ (10:00 AM to 2:00 PM). No _from_ before an en dash range.

**Decimals** Leading zero below one (0.5).

**Large numbers** _1.2 million_ in prose. _K, M, B_ only in tight UI, capitalized, no space (12K).

**Negative numbers** A minus sign (−), not a hyphen or an en dash.

**Ordinals** Spell out _first_ through _ninth._ Never _firstly._

## Dashes and hyphens

**Em dash (—)** Don't use it. The replacement table is in `SKILL.md`.

**En dash (–)** Number and date ranges only, no spaces. In a UI time range, spaces are fine (2:15 PM – 4:45 PM).

**Hyphen (-)** Hyphenate a compound before a noun and leave it open after the noun (_a well-known issue,_ but _the issue is well known_). No hyphen after an _-ly_ adverb (_a newly created project_). Most prefixes take no hyphen (_autoscale, preview, rerun, nonzero_). Hyphenate when the word would be misread (_re-create, re-sort_) or the next character is a capital or a numeral (_non-English, pre-2020_). Spell out suspended compounds (_first-level and second-level headings_). It's _email,_ not _e-mail._

## Punctuation

**Commas** Serial comma always (_chat, email, and video_). After an introductory phrase. Before _and, but,_ or _so_ when they join two full sentences. No comma between two verbs that share one subject (_The connector retries the request and logs the result_).

**Colons** Use one to introduce a list, inline or bulleted, when the lead-in is a full sentence or needs the items to finish it. Don't use one to attach an explanation to a sentence. Write two sentences. Lowercase after a colon unless the next word is a proper noun. In a heading or title, capitalize the word after it. Never at the end of a heading.

**Semicolons** Don't use them. Split the sentence or make a list.

**Quotation marks** Straight, never curly. Periods and commas go inside the closing mark. Exception: when the quoted text is a literal value, such as a search term or a file name, the punctuation goes outside (No projects match "sales".). No quotation marks for emphasis.

**Apostrophes** _'s_ for a singular possessive, even after _s_ (_the process's ID_). Only an apostrophe after a plural _s_ (_the members' roles_). No apostrophe for plurals (_APIs, 2020s_). No possessive on product names or acronyms. Rewrite: _answers from Acme Assistant, the API limits._

**Parentheses** For an aside the sentence could drop. Not nested. Period inside only when the whole sentence is in parentheses.

**Periods** One space after. End every full sentence, even a two-word one. None on headings, titles, UI labels, or list items that aren't full sentences.

**Slashes** Only for fixed pairs (_on/off, read/write_). Never as a substitute for _or._ Don't change slashes in paths or URLs.

**Ampersands** Write _and,_ unless the ampersand is part of a name or a UI label.

**Exclamation and question marks** No exclamation points in UI or documentation. A question is fine when the reader has a decision to make ("Delete this project?").

**Punctuation next to bold** takes the style of the sentence, not the label. In "Select **Save**, and then close the tab," the comma isn't bold.

## Proofreading sweep

The last pass before the fidelity check. Read the whole draft once per line below. Each pass looks for one kind of problem.

- **Spelling.** Misspellings. US spelling (_color, organize, center_). The same spelling of every term every time. Homophones a spell-checker misses (_their/there, its/it's, affect/effect, then/than, lose/loose_).
- **Doubled and dropped words.** "the the," "to to," a missing _a_ or _the_ left behind by an edit.
- **Agreement.** Subject with verb and pronoun with noun, especially across a long subject or a list. Collective nouns (_team, company_) are singular. With _or,_ the verb follows the nearest subject.
- **Tense drift.** A stray _will_ or _was_ in present-tense text that isn't about the future or the past.
- **Dangling modifiers.** "After saving the file, the dialog closes." The dialog didn't save anything.
- **Awkward phrasing.** Read the draft aloud. Rewrite any sentence you had to read twice, without changing what it says.
- **Punctuation.** Serial comma. Straight quotes. No period on headings or labels. No em dashes. No semicolons.
- **Capitalization.** Sentence case on headings. UI labels match the screen. Defined terms consistent.
- **Numbers.** Words below 10 in prose, numerals in UI, commas from four digits, _percent_ in prose and % in tables. Identifiers and versions untouched.
- **Links and cross-references.** Every link goes somewhere. Every "see X" names a section that exists.
