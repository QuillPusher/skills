# Terminology

Consistent names make a document read as one product. This file is the only source you use for names. Don't look a name up anywhere else. If a name isn't here, leave it as the source wrote it and flag it.

Tables of before and after show a rule. They are not phrases to find and replace.

## Canonical product names

Fill in this table with your own product names and the aliases to retire. Replace the aliases listed here with the canonical name. Don't guess at aliases that aren't listed.

| Write | Replace these aliases |
| --- | --- |
| _(your product name)_ | _(aliases to retire)_ |

**If the table holds only the placeholder row, skip this check.** Don't apply the example below to real content.

Example of a filled-in row, for a fictional product: **Acme Assistant** replaces _Acme Assist, AcmeBot, the assistant bot._ After the first mention in a section, _the Assistant_ is fine when the context is clear.

## Product name or generic capability

- The product name names your product.
- A generic term names the category. For an AI chat feature, that's **AI assistant** or **virtual assistant.** Use whichever the source uses most, and use it every time.
- Don't alternate among _assistant, bot, chatbot,_ and _agent_ for the same thing. _Agent_ can also mean a person.

> Acme Assistant answers questions about project status. (the product)
>
> An AI assistant can handle routine questions without a person stepping in. (the capability)

If a bare word in the source could mean either the product or the category, flag it instead of choosing.

## Third-party brands

Third-party platforms appear in integration and deployment content. Use the exact casing in the table everywhere.

In **documentation**, put the symbol on the first mention in the body of the file, not in headings. After that, the plain name. In **UI**, whether a symbol appears depends on the surface, not on which occurrence comes first. Functional UI takes none. The surface table is in `ui-text.md`.

If the source already shows a symbol, keep the symbol the source used. If the table says **Confirm**, add no symbol and flag it. Never switch ™ to ® or back on your own.

Replace these example rows with the brands your content names. Set the symbol only after checking the owner's trademark guidelines, and record the date you checked.

| Write it as | Owner | Symbol at first mention | Checked |
| --- | --- | --- | --- |
| **GitHub** | GitHub, Inc. | Confirm | Not yet |
| **Salesforce** | Salesforce, Inc. | Confirm | Not yet |
| **Slack** | Slack Technologies, LLC | Confirm | Not yet |
| **Jira** | Atlassian Pty Ltd | Confirm | Not yet |

If an owner restyles a brand, use the current form.

Don't use a brand as a verb or a common noun. "Slack me" becomes "Send me a message in Slack." Rewrite only when the meaning is clear. Otherwise, flag it.

> The connector supports ExampleCloud® and SampleChat® workspaces. ExampleCloud projects are imported automatically. (fictional brands)

**Attribution line.** If a documentation file names any third-party brand and has no trademark notice, add this line at the end and flag it for legal review: "All product and company names are trademarks or registered trademarks of their respective owners." Don't write "is a registered trademark of" for a brand the table marks Confirm.

Don't add a symbol to a term that isn't a brand. For your own names, follow your legal team's guidance. If you don't have it, flag rather than add.

## Defined terms

A term the document defines, in a glossary or a definitions section, keeps the capitalization its definition gave it everywhere afterward. A term the document doesn't define stays lowercase. Don't capitalize a term because it looks important, and don't assume a term is defined because it looks like one.

> A Maintenance Window is a scheduled period when updates can run. Create a Maintenance Window for each region.
>
> The backlog holds tasks that nobody has picked up yet. (not defined, so lowercase)

## Product terms must name real objects

A product term should name something the reader can see or act on. You can't check the screen. If a term reads like a feature name but nothing in the source shows it as a label, menu, or setting, flag it.

## Acronyms

- Spell out product and feature names. Never turn them into acronyms.
- On first use, spell out the term and put the acronym in parentheses. After that, the acronym alone within the same document or screen.
- Expand an acronym only if the expansion appears somewhere in the source. Otherwise flag it. Don't expand from memory.
- Skip the spelled-out form for acronyms every reader knows, such as USB, FAQ, URL, and PDF.
- If a term appears once, spell it out and skip the acronym.
- Don't introduce an acronym in a heading.
- Lowercase the spelled-out form unless it's a proper noun (_single sign-on (SSO)_).
- Plural: lowercase _s,_ no apostrophe (_three APIs_).
- _A_ or _an_ by sound: _an API, an SSO setting, a URL._
- No possessive: "the API's limits" becomes "the API limits."
- Replace Latin abbreviations per the Words table.

## Words

Words to use, words to avoid, and why. Check a draft against it. The Why column tells you when the rule doesn't apply. Add rows from your own review findings.

| Write | Instead of | Why |
| --- | --- | --- |
| **one generic term**, such as _AI assistant_ | alternating assistant, bot, chatbot, agent | Consistency. _Agent_ can also mean a person. |
| **you** | the user | One reader, addressed directly. _User_ stays as a category word. |
| **sign in** (verb), **sign-in** (noun) | log in, login | House style |
| **set up** (verb), **setup** (noun) | setup (as a verb) | The verb is two words |
| **email** | e-mail | Current spelling |
| **dialog** | dialog box, pop-up | Shortest clear term |
| **checkbox** | check box | Current spelling |
| **select** | click, tap | Works for every input method. Keys are still _pressed._ |
| **cyberattack**, **cyberthreat** | cyber attack, cyber-attack | One word |
| **use** | utilize, leverage | Plain word |
| **help** | facilitate, empower | Plain word. _Enable_ stays when it means turn on. |
| **through**, **by**, **using** | via | Plain word |
| **for example** | e.g. | Latin abbreviations confuse readers and translation tools |
| **that is** | i.e. | Same reason |
| **such as**, or name the items | etc. | Say what's included. If the source doesn't list the rest, flag it. |
| (flag, don't rewrite) | always, never, guarantees, ensures, eliminates, perfect, applied to an outcome or to model behavior | A claim, not a style choice. Suggest _selects, ranks, estimates, predicts, recommends,_ or a plain statement of what the product does. |
| (flag, don't rewrite) | understands, knows, believes, thinks, applied to a product | Products don't have minds. Suggest _ranks, selects, estimates._ |
| (delete) | very, really, quite, rather, actually, basically, simply, just, easily, truly, genuinely, literally | Filler intensifiers |
| (delete) | seamlessly, robust, powerful, intuitive, cutting-edge, best-in-class, world-class | Marketing words that carry no fact |
| (keep, or flag) | may, might, could, typically, usually, up to, at least | A hedge that states real behavior is a fact. Flag if you can't tell. Cut only when it's clearly filler. |

**Limit.** Delete a word from the delete rows only when it's working as an intensifier. _Just_ meaning "only" or "a moment ago," and _simply_ or _really_ inside a quotation or a product name, stay. In UI strings, a swap that would rename a label the product already uses everywhere, such as _Log in_ to _Sign in,_ is a product decision. Flag it rather than changing one screen.

## Capitalizing technology terms

Most technology terms are common nouns. Lowercase them (_cloud computing, machine learning, open source_). Capitalize a product name or a term the source consistently capitalizes. If you can't tell whether a capitalized word is a name, leave it and flag it.
