---
name: provenance-html-report
description: "Trace the text of a target document (generated, compiled, summarized or edited from other material) back to the source documents it came from, and produce a self-contained HTML review report. Each passage of the target appears on the left, with verbatim source excerpts on the right, plus how the passage was added, why it is included, a verdict (Verified, Minor drift, Overstates, Unsupported, Check), an automatic verbatim-quote check, review checkboxes and notes, verdict filters, and a term search that shows only the passages using a term. Use whenever the user wants to verify, audit, trace or fact-check where a document's text came from, check an AI-generated or compiled document against its sources, compare a document with its source material side by side, or asks for a provenance, traceability, source-mapping, citation or lineage report, even if they don't say provenance."
argument-hint: "<target (destination) document> <source files or folders...>"
---

# Provenance HTML report

The user names a **target document** and the **source documents** it was built from. This skill traces every passage of the target back to those sources and builds an HTML report the user can work through by hand to confirm two things: that each passage really came from where it claims, and that it represents that source accurately.

The core unit is a **unit**: a passage of the target that came from the same source(s), shown side by side with verbatim excerpts of those sources. The tracing is done by reading. `scripts/prov.py` extracts and chunks the target, converts sources to text, checks that the quotes are really verbatim, and builds the HTML from a fixed template.

**Never hand-write the report HTML or change its layout per job.** Layout changes belong in `TEMPLATE` in `scripts/prov.py` (see Maintenance).

## Files

| File | Use |
|---|---|
| `scripts/prov.py` | `doctor` the converters, `extract` the target into chunks, `totext` the sources, `check` the traced units, `build` the HTML. |
| `references/tracer-brief.md` | Template for the brief every tracer follows: the unit JSON schema, the verdicts, and the quoting rules. Fill it in for each job. |
| `example/` | A small worked example: fictional sources in six formats (`source/`), the target (`target/`), and the report built from them (`output-report.html`). Point users to it if they want to see an output first. |

Run it with the skill's path, e.g. `python "<skill dir>/scripts/prov.py" build <workdir>`.

## Conversion method (keep it the same every time)

The standard method:

| Files | Converter |
|---|---|
| Target and sources in .docx, .odt, .rtf, .epub | **pandoc**, to GitHub Markdown, which keeps headings, lists and tables |
| .html | **pandoc**, to plain text |
| PDFs | **pypdf**, or **pdftotext** if pypdf is missing |
| Slides | **python-pptx** |
| Spreadsheets | **openpyxl** |
| Markdown and text | read directly |

Don't swap in other converters: results should stay comparable between jobs.

## Required inputs: confirm them before anything else

Every job needs two things, and the user's request must identify both:

1. **The target (destination) document**: the one file whose text is traced, i.e. the generated, compiled or edited result.
2. **The source documents**: the files and/or folders the target was built from.

Before you run any command, check the request:

- **Both clearly named** (paths, file names, or an unambiguous reference such as "the report I just generated"): continue.
- **Either one missing or ambiguous**: stop and ask. Ask only for what's missing, in one short message. For example:
  - "Which file should I trace? (the target, e.g. `report-final.docx`)"
  - "Which source files or folders was `report-final.docx` built from?"
  - "I found three .docx files in this folder. Which one is the target?"

Never guess either input from the contents of a folder, from file names, or from earlier conversation that doesn't clearly name it. A wrong target or an incomplete source list makes the whole report misleading. Don't treat a source list as complete unless the user said so. If the user says "and anything else relevant", ask which folders that covers.

## Workflow

### 0. Set up

Once the target and the sources are confirmed, run the doctor on them:

```bash
python prov.py doctor "<target>" "<source folder>" ...
```

It lists the converters these files need and marks what is missing, with the install command.

- **Missing Python packages** (`pypdf`, `python-pptx`, `openpyxl`, `pypandoc_binary`): install them with `pip`. If your environment asks before installing software, ask the user first in one line, naming the packages.
- **Missing pandoc**: offer `pip install pypandoc_binary` first. It bundles pandoc, needs no admin rights, and the script finds it automatically. The system installer the doctor prints is the alternative. Ask the user before either, because it changes their environment.
- **If pandoc can't be installed** (no network, policy, or the user declines): tell the user, then run `extract` and `totext` with `--fallback`. The built-in reader covers .docx and .html only, with simpler tables and lists. The report header then says that a lower-fidelity conversion was used. Never use `--fallback` silently.
- **Python itself missing or older than 3.8**: the user has to install it; tell them.
- Re-run the doctor until it says **Ready**.
- **Optional full setup**: run `python prov.py doctor --all`. If it lists converters these files don't need, offer them once, in one line, as an option the user can decline: "Want me to also install `<packages>` so slides, spreadsheets and other formats work in future jobs?" Install only if the user says yes. Don't block the current job on this.

### 1. Pin down the job

The target and the sources were confirmed above. Get the rest from the conversation and the files, and ask only about what you can't work out, in one short round of questions:

- **Target version**: the exact file and version to trace. If it was edited after it was generated, trace the edited file. The report records the target's fingerprint and warns if the file changes later.
- **Sources**: the files and folders the target was built from. Anything not listed is out of bounds; a claim supported only by outside knowledge is reported as Unsupported, with a note.
- **Source rules (optional)**: whether some sources carry more weight than others. Examples:
  - In release documentation, only release notes and roadmaps prove a feature shipped; specs only define terms.
  - In a research summary, peer-reviewed papers outrank blog posts.
  - In a contract summary, the signed contract outranks drafts and emails.

  If the user has such a rule (in this conversation, memory or project instructions), use it. If the target makes claims where weight matters and no rule exists, ask. If all sources are equal, skip it.
- **Build history (optional)**: earlier drafts, notes, prompts, edit scripts or review comments. These explain *how* text was added. Without them, `how_added` describes the transformation instead, e.g. verbatim, paraphrased, combined from X and Y, or inferred.
- **Scope**: what to leave out, e.g. images, tables of contents, boilerplate, or document structure. The default is all body text, captions and table text.
- **Granularity**: unit by paragraph (the default), by sentence for high-stakes text, or by section for a quick pass.

### 2. Extract and chunk

```bash
python prov.py extract "<target>" "<workdir>" --words 1800
python prov.py totext "<source folder or file>" "<workdir>/srctxt"
```

- **Work folder**: use a work folder near the target, e.g. `<target folder>/_provenance/`.
- **What `extract` writes**: `doc.md`, `toc.md`, chunks of about 1,800 words (split at headings, or at paragraphs if the target has none), and a starter `report.json`.
- **What `totext` writes**: text copies of PDFs, office files, HTML and spreadsheets, plus `INDEX.md`, which maps each copy to its original. It lists files it couldn't convert, such as images and audio. Tell the user about those: they can only be cited by description, not quote-checked.
- **Check the chunks**: adjust them by hand if one is unbalanced. Long appendices, tables and reference lists deserve their own chunk.

### 3. Write the brief

Copy `references/tracer-brief.md` to `<workdir>/BRIEF.md` and fill in every placeholder:

- the target path
- the sources, grouped by weight if there are rules
- the build history
- the scope and granularity
- the source kinds to use

Tracers can't see this conversation, so give concrete paths.

### 4. Trace

- **Short targets** (one or two chunks): trace them yourself, following the brief.
- **Longer targets**:
  - Launch one subagent per chunk, all in one message, in the background, if your environment supports subagents. Keep to about 10 or fewer, merging small chunks.
  - Use this prompt: "Read `<workdir>/BRIEF.md` and follow it exactly. Your CHUNK is "A": file `<workdir>/chunk_A.md` (<what it covers>). Write `<workdir>/out/A.json`."
  - Without subagents, trace the chunks one after another yourself.
- **Progress**: as each chunk finishes, give the user a one-line update with its counts and the most important issue.

### 5. Check quotes

```bash
python prov.py check "<workdir>"
```

- **What it checks**: it validates every unit, splits each quote into sentence-sized fragments, and looks for them in the target text and in the cited source file. Matching is by words only, ignoring punctuation and case.
- **What it records**: found, partly found or not found on each unit. The report tags the misses.
- **When the tracer needs to fix it**: many misses in one chunk mean that tracer paraphrased, so send it back to quote verbatim.
- **When to leave it**: a few misses from PDF line breaks, escaped text in code files, or tables are normal. Leave them tagged for the reviewer.
- **Duplicate ids and a changed target**: the check also warns about both.

### 6. Configure and build

Edit `<workdir>/report.json`:

| Key | Meaning |
|---|---|
| `title` | Report heading |
| `document` | Target name shown in the intro |
| `doc_label` | Left-column heading (default "In the target document") |
| `why_label` | Label for the inclusion reason, e.g. "Why it is in the summary" |
| `evidence_label` | Label for each unit's strongest support, e.g. "Strongest support" or "Authority" |
| `evidence_rule` | One or two sentences stating the source rules, or leave it empty |
| `scope_note` | What was left out of the trace |
| `strong_kinds` / `weak_kinds` | Source kinds tinted green (carry weight) or red (context only) |
| `output` | Where to write the HTML. Put it where the user can open it. |
| `target_fingerprint`, `target_converter` | Set by `extract`; don't edit |

```bash
python prov.py build "<workdir>"
```

### 7. Report back

1. Lead with the report link and the counts per verdict.
2. Then give the recurring issues, ranked by impact:
   - sources that conflict
   - claims that rest only on weak sources
   - the writer's own inferences presented as sourced
   - overstatements
   - text with no source at all
3. Say that the verdicts are machine-assisted and the report is for the user's manual check.
4. Don't change the target or the sources unless asked.

## What the reviewer gets

- **Unit cards**: one per unit. The target text is on the left. The source excerpts are on the right, each with its kind, file and locator. Below them are how it was added, why it is included, and a highlighted note on anything to check.
- **Items to look at first**: every Overstates, Unsupported and Check unit, linked.
- **Review tools**: verdict filter chips, and a Reviewed checkbox and notes box on every unit, saved in the browser. Ticking Reviewed collapses the unit to a single row, which Expand reopens. **Hide reviewed** at the top hides reviewed units altogether, and reviewed items are greyed out in "Items to look at first". A progress count and Export and Import of review notes as JSON let the review move between browsers or people.
- **Term search**: type a term to show only the passages that contain it, highlighted, with a match count. Choose whether to search the target text (every passage that uses a term, and where each came from), the source excerpts, or the how/why text and the reviewer's notes. It supports whole-word matching, and Esc clears it. Combine it with the verdict chips, e.g. only Check units that mention a term.
- **Header details**: the traced version (date and hash), the quote-check totals, and a warning if the built-in fallback reader was used for any file.

## Limits to tell the user about when they apply

- **Verbatim excerpts**: the report quotes sources word for word. Sharing it shares those excerpts, so check confidentiality before sending it on.
- **Images, audio and video**: these sources can't be quote-checked; tracers cite them by description.
- **Web pages**: they change. Save a copy and trace the copy.
- **Translated or heavily summarized text**: quote matching fails by design. The verdict and note carry the judgement.
- **Text pandoc can't extract**: text boxes, comments, tracked changes (pandoc shows the accepted version), headers and footers may be missing from `doc.md`. Say so if the target relies on them.
- **Re-runs**: review notes are keyed by unit id. Re-chunking changes ids and orphans old notes, so export notes before re-tracing.

## Maintenance

If the user keeps a versioned source copy of this skill separate from the installed copy, edit the source first, then copy the whole folder over the installed one so the two stay identical.
