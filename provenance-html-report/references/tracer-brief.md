# Provenance tracing brief (template)

Copy this file to `<workdir>/BRIEF.md` and replace every `<<...>>` placeholder before you hand it to tracers. Delete any optional section that doesn't apply. Tracers read only this brief and their chunk, so it must stand alone.

---

# Provenance tracing brief

**Goal.** A reviewer will manually check the text provenance of the target document `<<target path>>`. Its full text is in `<<workdir>>/doc.md`, and the chunk list with headings is in `<<workdir>>/toc.md`. For each passage they need four things:
- where it came from, as a verbatim source excerpt
- whether it represents that source accurately
- how it got into the target
- why it is included

**Scope.** Trace <<all body text, captions and table text / ...>>. Leave out <<e.g. images, table of contents, boilerplate>>.

**Granularity.** <<Paragraph (default) / sentence / section>>. Group consecutive text into one unit only if it came from the same source(s). Split a paragraph into several units if parts came from different sources. Every in-scope sentence must belong to some unit.

## Sources

Only the sources below count. If a passage relies on anything else (general knowledge, the writer's own reasoning), report it as such; don't go looking outside this list.

<<If some sources carry more weight than others, keep the two groups below and state the rule. Otherwise merge them into one list.>>

**Sources that carry weight** (<<the rule, e.g. "only these can confirm that a statement is true or in scope">>):
- <<kind>>: `<<path>>`, <<what it covers>>

**Context sources** (definitions, background and wording; they can't confirm a claim on their own):
- <<kind>>: `<<path>>`

**Non-text sources** (optional): <<images / recordings>> in `<<folder>>`. <<Transcriptions, if any: path>>. Cite the file name and describe or transcribe what it shows. You may open images to read them.

**Build history** (optional; explains HOW text was added): <<earlier drafts in order, notes, prompts, edit scripts, review comments>>. <<Start with X; it maps most claims to sources.>>

Text copies of PDFs, office files, HTML and spreadsheets are in `<<workdir>>/srctxt/` (see `INDEX.md` there). Quote from the text copy, but cite the ORIGINAL file path. Search the sources with grep or your search tool rather than reading everything.

## Rules

- Quote VERBATIM, in both directions. `doc_excerpt` is copied from the chunk, and source excerpts are copied from the source. Trim with "…" but never paraphrase inside a quote. A checker searches for every fragment, so paraphrases get flagged.
- Give a locator for each excerpt: a line number, heading, page, slide, sheet or timestamp.
- Never mark a unit Verified unless you found the quote yourself.
- If sources disagree, quote both and use the verdict Check.
- Name the writer's own additions plainly in `how_added` and `note`: inferred explanations, examples, generalisations, softened or strengthened claims.
- Don't edit the target or any source.

## Output

Write JSON (UTF-8) to `<<workdir>>/out/<CHUNK>.json`, with units in document order:

```json
{"chunk": "<CHUNK>", "units": [{
  "id": "3.2-1",
  "section": "3.2 Pricing tiers",
  "label": "Intro paragraph",
  "doc_excerpt": "verbatim text from the chunk (trim long passages with …)",
  "sources": [{"file": "path exactly as listed above", "locator": "L120 / p. 4 / slide 7 / image-12.png",
               "excerpt": "verbatim", "kind": "<<one of the source kinds above>>"}],
  "how_added": "1-2 sentences: copied verbatim from …, paraphrased from …, combined from X and Y, inferred by the writer, added in draft N …",
  "why_included": "1-2 sentences: why this belongs in the target, with a short quote from the source that justifies it. Say plainly if nothing does.",
  "evidence": "the kind of the strongest supporting source, or 'Context source only' or 'None found'",
  "verdict": "Verified | Minor drift | Overstates | Unsupported | Check",
  "note": "what the reviewer should check: wording drift, conflicts, the writer's inferences. Empty if clean."
}]}
```

- `id` must be unique across the whole target: use the section number, a hyphen and a sequence number (or the chunk letter and a sequence if there are no section numbers). `section` is the heading exactly as in `toc.md`.
- `sources` may be empty only when the verdict is Unsupported.

Verdicts:
- **Verified**: faithful to its source, and the source counts as support under the rules.
- **Minor drift**: a small difference in wording or emphasis that doesn't change the meaning.
- **Overstates**: the target claims more, or more certainly, than the source.
- **Unsupported**: no listed source supports it.
- **Check**: sources conflict, or you couldn't confirm it.

Check that the JSON parses, for example `python -c "import json;json.load(open(r'<file>',encoding='utf-8'))"`. Then reply with only the unit count, the count per verdict, and the 3 most important issues.
