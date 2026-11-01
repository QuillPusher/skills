---
name: anything-to-html
description: "Convert documentation into clean, accessible HTML with a fixed template (daylight and night themes, header with search, collapsible sidebar, steps, callouts, tables, screenshots). Takes Word (.docx), PDF (including scanned, with OCR), PowerPoint (.pptx), Excel/CSV, Markdown, ODT/RTF/EPUB/HTML, pasted text, or new writing and produces either ONE self-contained HTML file (images embedded, sidebar of chapters) or a multi-page help site (one page per topic, hub pages, Previous/Next, help-map.json for in-app Help links). The look comes from a template that a build script applies, so every output matches. Checks which converters are installed only with the user's consent and never installs anything without approval. Use whenever the user asks to convert, export, publish or turn a document into HTML, a web page, web help, online help, a help site, or in-app help, or to create any new HTML documentation page."
argument-hint: "[source file(s) or folder] [single|site]"
---

# anything-to-html

Turn documentation into HTML that looks exactly like the template. The template owns all styling and behaviour, including the daylight/night theme toggle. You write only the **content** (what goes inside `<main>`) using the template's component classes; `scripts/build_html.py` wraps it in the template's exact CSS, JS, header, sidebar and footer; `scripts/check_html.py` confirms nothing drifted.

**Never write or edit CSS or JavaScript, never use `style=""`, never invent class names.** If something can't be expressed with the existing components, tell the user rather than styling it.

## Files

| File | Use |
|---|---|
| `assets/html-doc-template.html` | The template and component gallery. **Read it before writing any content**; copy component markup from its `COMPONENT:` blocks exactly. |
| `scripts/check_env.py` | Reports which converters are installed and what each input format can be converted with. Read-only. Run it only with the user's consent (Step 0). |
| `scripts/extract_pdf.py` | PDF → Markdown + images (headings, lists, tables, OCR for scanned pages). Needs PyMuPDF. |
| `scripts/ocr_windows.ps1` | OCR with the Windows 10/11 built-in engine. Used by `extract_pdf.py --ocr windows`. No install. |
| `scripts/ocr_macos.swift` | OCR with Apple Vision on macOS. Used by `extract_pdf.py --ocr macos`. Needs only the Xcode Command Line Tools. |
| `scripts/build_html.py` | Builds output from fragments: `single` or `site` mode. |
| `scripts/check_html.py` | Validates built files. Must pass before delivery. |
| `references/site-mode.md` | `nav.json` format and page rules for multi-page help sites. Read it only for site mode. |

Paths below are relative to this skill's folder. Python 3.8+ (standard library) for build and check. Works on Windows, macOS and Linux: where this file says `python`, use `python3` if that is the command on the machine. On Windows, set `PYTHONIOENCODING=utf-8` if output looks garbled.

## Step 0: Tools and consent

Converters are external programs on the user's machine. Follow this order; never skip the questions.

1. **Work out what the source needs** from the table in Step 2 (for example a text PDF needs PyMuPDF; a .pptx needs pandoc).
2. **Ask before scanning.** Ask the user one question: do they know whether those tools are installed, or may you run `python scripts/check_env.py` to find out? Say that it only reads versions and installs nothing. Don't look for installed software until they say yes; if they prefer to tell you, go by their answer.
3. **With consent, run** `python scripts/check_env.py` (add `--json` if you want to parse it). It lists what works now and, for anything missing, the install options with the exact command, the licence and the size.
4. **If the source is covered, continue to Step 1.** If not, give the user the options as a short numbered list and let them choose. Always include the no-install options where they exist: ask for the original editable file (a PDF made from Word is better converted from the .docx); use the OS's own OCR for scanned PDFs (Windows built-in engine; Apple Vision on macOS, which needs only the Xcode Command Line Tools); use pandoc's own readers for .pptx/.xlsx/.odt/.rtf/.epub when pandoc is present.
5. **Install only after an explicit yes**, with the exact command `check_env.py` showed, then re-run `check_env.py` and continue. Never install on your own initiative, never add `pip install` to a script, and never upgrade or remove anything.
6. **Host document skills.** If your environment has document skills (for example Claude Code's `pdf`, `docx`, `pptx`, `xlsx`), they are instructions and helper scripts, not converters: they rely on the same tools (`pandoc`, `pdfplumber`, `markitdown`, LibreOffice). `check_env.py` reports those tools when present. Use such skills for editing the source format (tracked changes, comments), not for conversion.

## Step 1: Choose the output mode

| Mode | Choose when | Output |
|---|---|---|
| `single` (default) | "Convert this doc to HTML", one guide to share, email or attach | One `.html` file, images embedded, sidebar lists chapters (h2) and topics (h3), position tracking while scrolling |
| `site` | "Web help", "help site", "online help", "in-app help", or the user wants one page per topic or app-route mapping | A folder of pages + `images/` + `help-map.json` |

If the request doesn't say and the source is a single document, use `single`. Ask only if the user mentions both.

## Step 2: Get the source content

Create a working folder next to where the output will go, named `<output-name>-src/`. Keep it after delivery; it lets the user rebuild after edits. Run the commands below from inside it so image paths come out relative to it.

| Input | First choice | If that tool is missing |
|---|---|---|
| **.docx** | `pandoc "<source.docx>" -t html5 --wrap=none --extract-media=media -o raw.html` | `markitdown`, or unzip the .docx (`word/document.xml`, images in `word/media/`) |
| **Several chapter .docx files** | Run pandoc once per file with its own media folder (`--extract-media=media-01 -o raw-01.html`, ...), because pandoc names every file's images `image1.png`, `image2.png`, ... | same |
| **PDF with a text layer** | `python <skill>/scripts/extract_pdf.py "<source.pdf>" --out .` → `raw.md` + `media/`, then `pandoc raw.md -t html5 --wrap=none -o raw.html` | `markitdown`, `pdftotext -layout` or `pypdf`: plain text only; rebuild the structure by hand |
| **Scanned PDF** (no text layer) | Same command; scanned pages are OCR'd with `--ocr auto` (tesseract if installed, else the Windows built-in engine, else Apple Vision on macOS). OCR gives text, not structure: rebuild headings, lists and tables from the page images in `media/` | Ask for the original file, or offer tesseract (Windows, macOS, Linux); on macOS without `swift`, offer `xcode-select --install` |
| **.pptx** | `pandoc "<deck.pptx>" -t html5 --wrap=none --extract-media=media -o raw.html` (one `<h2>` per slide title) | `markitdown`, or `python-pptx` |
| **.xlsx / .csv / .tsv** | `pandoc "<book.xlsx>" -t html5 --wrap=none -o raw.html` (one table per sheet); ask which sheets and columns matter if the file is large | `markitdown`, `openpyxl`, or Python's `csv` module |
| **.odt, .rtf, .epub, .html, Jupyter, Jira/Confluence wiki** | `pandoc "<file>" -t html5 --wrap=none --extract-media=media -o raw.html` | HTML: read it directly |
| **Markdown** | `pandoc "<source.md>" -t html5 --wrap=none -o raw.html`, or write the fragment directly | write the fragment directly |
| **Pasted text, notes, or new writing** | Write the fragment directly | – |
| **Images or screenshots only** | Look at them and write the content; they become `.screenshot` figures | – |

**Look at every image** (open the files) so you can write real alt text and spot screenshots that need attention. For a PDF, `extract_pdf.py --render` also writes `pages/pNN.png` so you can see the original layout when a table or figure is unclear.

## Step 3: Write the content fragment(s)

A fragment is only the inner content of `<main>`: no `<html>`, `<head>`, `<body>`, `<style>` or `<script>`. In single mode write one `content.html` in the working folder. In site mode write one file per page in `src/`, named like the output page.

**Heading levels**

| Source | Single file, one document | Single file, multi-chapter guide | Site page |
|---|---|---|---|
| Document title | `.cover` `<h1>` | `.cover` `<h1>` (guide title) | `.cover` `<h1>` (topic title) |
| Heading 1 / PDF `#` / slide section | `<h2>` in a `<section>` | `<h2 data-icon="...">` per chapter | Section hub (in `nav.json`) |
| Heading 2 / PDF `##` / slide title | `<h3>` | `<h3>` | One page per topic |
| Heading 3 / PDF `###` | `<h4>` | `<h4>` | `<h2>` in a `<section>` |
| Heading 4 / PDF `####` | bold `<p><strong>` | bold `<p><strong>` | `<h3>` |

Chapter icons (`data-icon`, also used in `nav.json`): `home user users tool book clock download plus bolt chat shield check chart trend send settings file`.

**Content mapping**

| Source content | Component (copy markup from the template) |
|---|---|
| Title, summary, date, audience, version | `.cover` with `.eyebrow`, `h1`, `.subtitle`, `.meta-row` |
| Numbered procedure ("1. Select...", "Step 1") | `.steps` > `.step` with `.step-num`, `.step-title` (the action) and optional `.step-desc` (detail or result). Number from 1 in every `.steps` block. |
| Note, Info, Tip | `.callout.info` |
| Important, Caution, Warning | `.callout.warning` |
| Result, "you should now see", expected outcome | `.callout.success` |
| List of key points, prerequisites, "Important notes" | `.assistant-box` with a `.label` |
| Field/option/setting descriptions, spreadsheet rows | `<table>` with header row; add a Required column with `.req-yes` / `.req-opt` only if the source states it |
| Screenshot or diagram | `<figure class="screenshot">` with `<img src alt>` and `<figcaption>`. Put it inside the step's `.step-desc` if it shows that step, otherwise right after the paragraph that refers to it. |
| UI labels (buttons, menus, fields) | `<strong>` |
| File names, values, code | `<code>` |
| Bullets / ordered non-procedure lists | `<ul>` / `<ol>` |
| Cross-reference | `<a href="#heading-id">` (single) or `<a href="page.html#id">` (site) |
| Open questions in a draft | `.oq-row` table with `.status-open` (drafts only) |

**Pandoc clean-up** (always needed for .docx, .pptx, .odt):
- Drop the document's own table of contents (`<h1 class="TOC-Heading">Contents` and the list after it); the sidebar replaces it.
- Drop empty headings (pandoc gives them ids like `section`, `section-1`).
- Remove every `style=""`, `class` values pandoc invents, and `<span>` wrappers with no meaning.
- Keep the document's display size for images: pandoc writes it as `style="width:2.72in;..."`; replace that with a `width` attribute in pixels (inches × 96, rounded), for example `width="261"`. Without it, screenshots show at full resolution and look oversized. Images wider than the page shrink to fit automatically.
- Pandoc's `alt` text is often an auto-generated caption such as "AI-generated content may be incorrect". Replace it.
- `<blockquote>` usually means indentation: turn it into a plain paragraph, or a callout if it is a note.
- `<del>` is strikethrough text. Don't publish it silently: leave it out and list it in your report so the user can confirm.
- Leave out headers, footers and page numbers.

**PDF clean-up** (after `extract_pdf.py`):
- Heading levels are guessed from font sizes (see `extract-report.json`); check them against the document's own numbering and fix the levels.
- Drop the `<!-- page N -->` markers, the table of contents (lines with dot leaders and page numbers), and any header or footer line the script didn't catch.
- Paragraphs split by a page break arrive as two paragraphs: join them. Bulleted lines may arrive as one paragraph: split them.
- Images: drop logos and decorations; keep screenshots and diagrams. Images that the PDF stored as vector drawings are not extracted; use `--render` and tell the user which figures need a replacement.
- Tables that the script didn't detect arrive as lines of text; rebuild them from the page render.
- OCR text (scanned pages): expect a few character errors (`l`/`1`, `0`/`O`, `rn`/`m`); correct only what is unambiguous and list the rest in the report.

**PPTX clean-up**: pandoc gives one `<h2>` per slide title and the bullets under it; group slides into logical sections, promote the section-divider slides to chapters, and drop slide numbers, speaker notes and template footers. One slide image per slide is usually a screenshot; decorative images are not.

**Fidelity rules**
- Change structure and markup, never facts. Keep the source wording; don't add, drop, or "improve" content. Offer a separate wording pass afterwards if the user wants one.
- Keep every image unless the user says otherwise. Never edit images. If a screenshot shows something that looks like real customer data or an unfinished UI, flag it.
- Write alt text that says what the screenshot shows ("Settings page with the Profile tab open"), not "image1".
- Anything you can't map cleanly (a complex table, an embedded object, a diagram made of shapes): keep what you can and list it in the report.

## Step 4: Build

Single file:
```
python scripts/build_html.py single "<work>/content.html" --out "<output>.html" --product "<Product>" [--title "<Page title>"] [--header-title "<Header text>"]
```
Header text defaults to "<Product> Documentation"; page title defaults to the cover `<h1>`. Images are embedded; use `--no-embed` only if the user wants a separate images folder (then ship the images next to the file).

Site: write `nav.json` as described in `references/site-mode.md`, then:
```
python scripts/build_html.py site "<work>/nav.json" --src "<work>/src" --out "<output-folder>"
```

The daylight/night toggle, search, sidebar and "On this page" list come from the template; nothing to add.

## Step 5: Check, fix, re-check

```
python scripts/check_html.py "<output>.html"        (or the output folder)
```
Fix every ERROR in the **fragment** (never in the built file), rebuild, and re-run until it passes. Fix WARNINGS unless they reflect the source (for example, the source really has no h2 in a section); mention the ones you leave.

Then look at the result: the top of the page, a procedure, a table and a screenshot. If you have no browser tool, take a screenshot with headless Chrome or Edge and read the PNG (use a fresh `--user-data-dir` for each run; add `--force-dark-mode` to see the night theme). `check_env.py` prints the browser path; typical ones:
```
<browser> --headless=old --no-sandbox --disable-gpu --user-data-dir="<temp dir>" --window-size=1440,1800 --screenshot="<temp dir>/shot.png" "file:///<absolute path to output.html>"

Windows  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
macOS    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   (or ".../Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
Linux    google-chrome   (or chromium)
```
If neither works, ask the user to open the file.

## Step 6: Report

Tell the user, briefly:
- where the output is (link to it) and where the working folder is
- the mode, and the page or chapter count
- which converter was used, and anything installed (with their approval) during Step 0
- anything you didn't carry over or that needs a decision: strikethrough text, unmappable content, suspicious screenshots, images without a clear purpose, OCR doubts, remaining warnings
- how to rebuild after edits: edit the fragment, re-run the build command

## Creating new HTML docs (no source document)

Same flow from Step 3: plan the outline with the user if it isn't clear, write fragments with the components above, build, check. For a new home page in site mode, copy the landing blocks (`lp-hero`, `lp-section`, `lp-grid-3`, `lp-grid-2`, `lp-links-card`) from the template.

## Changing the look

Only by editing `assets/html-doc-template.html`: the token values in `:root` (daylight) and `html[data-theme="dark"]` (night). Every later build picks the change up, and `check_html.py` compares output against the template, so files built with the old version will fail the check until rebuilt. Keep the `BUILD:SIDEBAR` and `BUILD:MAIN` markers.
