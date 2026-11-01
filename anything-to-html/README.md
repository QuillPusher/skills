[![](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# anything-to-html

A skill for coding agents (Claude Code, Codex and similar) that turns documentation into clean, human-readable HTML with organized and segmented information for quick comprehension of large (often AI-produced) documents.

## Input and output

| Input | Converted with |
|---|---|
| Word (.docx), one file or chapter files | pandoc |
| PDF with a text layer | PyMuPDF via `scripts/extract_pdf.py` (headings, lists, tables, images) |
| Scanned PDF | same, plus OCR: tesseract if installed, else the OS engine with no install (Windows 10/11 built-in; Apple Vision on macOS via the Xcode Command Line Tools) |
| PowerPoint (.pptx), Excel (.xlsx), CSV, ODT, RTF, EPUB, HTML, Jupyter | pandoc |
| Markdown, pasted text, nothing (new writing) | written directly |

| Output | What you get | Good for |
|---|---|---|
| **Single file** (default) | One self-contained `.html`; images embedded; sidebar of chapters that follows your position | Email, chat, intranet, release attachments |
| **Help site** | One page per topic, hub pages, breadcrumbs, Previous/Next, `images/`, `help-map.json` (app screen → help page) | Hosted online help, in-app Help links |

Both outputs have a daylight/night toggle in the header. It follows the operating system setting until the reader picks one, then remembers the choice. Text colours meet WCAG AA contrast in both themes; the page has a skip link, visible focus outlines and respects reduced-motion settings.

The agent never writes styling. It maps the content onto the template's components, `build_html.py` wraps it in the template's CSS and JS, and `check_html.py` fails the output if styling was changed, a class was invented, a link or image is broken, or a screenshot has no alt text. Wording and facts are kept as in the source; anything that couldn't be carried over is reported.

## Tools and consent

The skill does not install software on its own. The agent:

1. asks whether you know which converters are installed, or whether it may run `scripts/check_env.py` to find out (read-only, a few seconds);
2. shows what works now and, for anything missing, the options with the exact install command, licence and size, including no-install alternatives;
3. installs only after you say yes, then re-checks.

Minimum: Python 3.8+. [Pandoc](https://pandoc.org) covers most formats; [PyMuPDF](https://pymupdf.readthedocs.io) (`pip install pymupdf`) covers PDF. Everything else is optional.

Platforms: Windows, macOS and Linux. The scripts are standard-library Python with pathlib and subprocess, the install hints are per OS (winget, brew, apt), and `check_env.py` finds the browser on each. Verified end to end on Windows; the macOS Vision OCR script has not yet been run on a Mac, so treat its first run as a test and report problems. These tools are called as external programs, not bundled; their own licences apply (pandoc GPL-2.0+, PyMuPDF AGPL-3.0, tesseract Apache-2.0, markitdown MIT).

## Use

Copy this folder to `~/.claude/skills/anything-to-html` (or your agent's skills folder), then ask, for example:

- "Convert `user-guide.docx` to HTML"
- "Turn `feature-spec.pdf` into a help site"
- "Create an HTML help page for the Invoices feature"
- `/anything-to-html path/to/guide.docx single`

The agent keeps a working folder `<output-name>-src/` next to the output. To update the HTML later, edit the content fragment there and re-run the build command the agent reported, or ask again.

## Folder contents

| Path | Purpose |
|---|---|
| `SKILL.md` | The instructions the agent follows |
| `assets/html-doc-template.html` | The template; open it in a browser to see every component |
| `scripts/check_env.py` | Reports installed converters and install options; changes nothing |
| `scripts/extract_pdf.py`, `scripts/ocr_windows.ps1`, `scripts/ocr_macos.swift` | PDF → Markdown + images; OS OCR helpers for Windows and macOS |
| `scripts/build_html.py` | Builds a single file or a site from content fragments |
| `scripts/check_html.py` | Checks built files against the template |
| `references/site-mode.md` | `nav.json` format for help sites |
| `LICENSE` | This project is licensed under the [MIT License](LICENSE) |

## Without an agent

```
python scripts/check_env.py
python scripts/extract_pdf.py guide.pdf --out guide-src
python scripts/build_html.py single content.html --out guide.html --product "Acme"
python scripts/build_html.py site nav.json --src src --out site
python scripts/check_html.py guide.html
```

A content fragment is the inner HTML of the page body: a `.cover` block, then `<section>` blocks with `<h2>` headings, using the classes shown in the template.

## Changing the brand

Edit only the token values in `assets/html-doc-template.html`: `:root` for daylight, `html[data-theme="dark"]` for night. Later builds pick the change up; files built with the old version fail `check_html.py` until rebuilt. Keep the `BUILD:SIDEBAR` and `BUILD:MAIN` markers.

## Licence

This project is licensed under the [MIT License](LICENSE). In plain terms: You can use, copy, modify, and even sell this software for free — just keep the copyright notice and license text with it, and understand it comes with no warranty.
