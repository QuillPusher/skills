"""Provenance report toolkit: extract and chunk a target document, convert sources to text,
check quotes in traced units, and build the HTML review report.

Usage:
  python prov.py doctor  <target> <source file or folder> ...   check the converters these files need
  python prov.py doctor  --all [files...]                       also list every optional converter
  python prov.py extract <target document> <workdir> [--words 1800] [--fallback]
  python prov.py totext  <source file or folder> <workdir>/srctxt [--fallback]
  python prov.py check   <workdir>
  python prov.py build   <workdir>

Conversion: pandoc is the primary converter for .docx/.odt/.rtf/.epub/.html (a system pandoc, or the
one bundled with `pip install pypandoc_binary`). pypdf (or pdftotext) reads PDFs, python-pptx slides,
openpyxl spreadsheets. If pandoc can't be installed, --fallback uses a simpler built-in reader for
.docx and .html; the report then says so in its header.

Work folder layout (created by `extract`):
  doc.md          full text of the target document (Markdown)
  toc.md          chunk list with the headings in each chunk
  chunk_A.md ...  the target split at top-level headings (or paragraphs if it has none)
  out/            one <CHUNK>.json per chunk, written by the tracers
  report.json     report settings (title, labels, rules, output path, target fingerprint)
"""
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter, OrderedDict
from datetime import date, datetime
from pathlib import Path

TEXT_EXT = {".md", ".markdown", ".txt", ".csv", ".json", ".yaml", ".yml", ".py", ".js", ".ts", ".xml", ".log", ".tsv",
            ".rst", ".tex", ".srt", ".vtt", ".sql", ".ini", ".toml"}
VERDICTS = ["Verified", "Minor drift", "Overstates", "Unsupported", "Check"]
VCLS = {"Verified": "ok", "Minor drift": "drift", "Overstates": "over", "Unsupported": "unsup", "Check": "check"}


# ---------------------------------------------------------------- text conversion
PANDOC_EXT = {".docx", ".odt", ".rtf", ".epub", ".html", ".htm"}
FALLBACK_EXT = {".docx", ".html", ".htm"}
ALLOW_FALLBACK = False   # set by --fallback
CONVERTER = {}           # resolved path -> converter used, for the report header


def pandoc_path():
    """A system pandoc, or the binary bundled with pypandoc_binary (installs without admin rights)."""
    p = shutil.which("pandoc")
    if p:
        return p
    try:
        import pypandoc
        p = pypandoc.get_pandoc_path()
        return p if p and Path(p).exists() else None
    except Exception:
        return None


def install_hint(tool):
    os_name = sys.platform
    if tool == "pandoc":
        system = ("winget install --id JohnMacFarlane.Pandoc -e" if os_name.startswith("win")
                  else "brew install pandoc" if os_name == "darwin" else "sudo apt-get install pandoc")
        return f"pip install pypandoc_binary  (no admin rights needed)  or  {system}"
    return {"pypdf": "pip install pypdf", "python-pptx": "pip install python-pptx", "openpyxl": "pip install openpyxl"}[tool]


def pandoc(path, fmt="gfm"):
    exe = pandoc_path()
    if not exe:
        if ALLOW_FALLBACK and Path(path).suffix.lower() in FALLBACK_EXT:
            CONVERTER[str(Path(path).resolve())] = "built-in fallback"
            return docx_fallback(path) if Path(path).suffix.lower() == ".docx" else html_fallback(path)
        raise SystemExit(f"pandoc is needed for {path}. Install it with: {install_hint('pandoc')}. "
                         "If it can't be installed, re-run with --fallback (lower fidelity for .docx and .html).")
    r = subprocess.run([exe, str(path), "-t", fmt, "--wrap=none"], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise SystemExit(f"pandoc failed on {path}: {r.stderr[:300]}")
    CONVERTER[str(Path(path).resolve())] = "pandoc"
    return r.stdout


def docx_fallback(path):
    """Standard-library .docx reader: headings, list items, paragraphs and tables as Markdown."""
    import xml.etree.ElementTree as ET
    import zipfile
    W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    z = zipfile.ZipFile(path)
    names = {}
    if "word/styles.xml" in z.namelist():
        for st in ET.fromstring(z.read("word/styles.xml")).iter(W + "style"):
            n = st.find(W + "name")
            names[st.get(W + "styleId")] = (n.get(W + "val") if n is not None else "").lower()

    def ptext(p):
        return "".join(t.text or "" for t in p.iter(W + "t"))

    out = []
    for el in ET.fromstring(z.read("word/document.xml")).find(W + "body"):
        if el.tag == W + "p":
            t = ptext(el).strip()
            if not t:
                continue
            ppr = el.find(W + "pPr")
            sid, is_list = "", False
            if ppr is not None:
                ps = ppr.find(W + "pStyle")
                sid = ps.get(W + "val") if ps is not None else ""
                is_list = ppr.find(W + "numPr") is not None
            name = names.get(sid, sid.lower())
            m = re.match(r"heading\s*(\d)", name)
            out += ["#" * int(m.group(1)) + " " + t if m else "# " + t if name == "title" else ("- " + t if is_list else t), ""]
        elif el.tag == W + "tbl":
            for i, tr in enumerate(el.iter(W + "tr")):
                cells = [" ".join(ptext(p) for p in tc.iter(W + "p")).strip().replace("|", "\\|") for tc in tr.findall(W + "tc")]
                out.append("| " + " | ".join(cells) + " |")
                if i == 0:
                    out.append("|" + "---|" * len(cells))
            out.append("")
    return "\n".join(out)


def html_fallback(path):
    """Standard-library HTML reader: text with headings and list items marked."""
    from html.parser import HTMLParser

    class P(HTMLParser):
        def __init__(self):
            super().__init__()
            self.out, self.skip = [], 0

        def handle_starttag(self, tag, attrs):
            if tag in ("script", "style"):
                self.skip += 1
            elif re.fullmatch(r"h[1-6]", tag):
                self.out.append("\n\n" + "#" * int(tag[1]) + " ")
            elif tag == "li":
                self.out.append("\n- ")
            elif tag in ("p", "div", "br", "tr", "section", "article", "table"):
                self.out.append("\n\n" if tag in ("p", "div", "section", "article", "table") else "\n")
            elif tag in ("td", "th"):
                self.out.append(" | ")

        def handle_endtag(self, tag):
            if tag in ("script", "style") and self.skip:
                self.skip -= 1

        def handle_data(self, data):
            if not self.skip:
                self.out.append(re.sub(r"\s+", " ", data))

    p = P()
    p.feed(Path(path).read_text(encoding="utf-8", errors="ignore"))
    return re.sub(r"\n{3,}", "\n\n", "".join(p.out)).strip()


def pdf_text(path):
    try:
        from pypdf import PdfReader
        CONVERTER[str(Path(path).resolve())] = "pypdf"
        return "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
    except ImportError:
        pass
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, encoding="utf-8")
        CONVERTER[str(Path(path).resolve())] = "pdftotext"
        return r.stdout
    raise SystemExit(f"A PDF reader is needed for {path}. Install it with: {install_hint('pypdf')}")


def pptx_text(path):
    try:
        from pptx import Presentation
    except ImportError:
        raise SystemExit(f"python-pptx is needed for {path}. Install it with: {install_hint('python-pptx')}")
    CONVERTER[str(Path(path).resolve())] = "python-pptx"
    out = []
    for i, slide in enumerate(Presentation(str(path)).slides, 1):
        out.append(f"## Slide {i}")
        for sh in slide.shapes:
            if sh.has_text_frame:
                out.append(sh.text_frame.text)
        if slide.has_notes_slide:
            out.append("Notes: " + slide.notes_slide.notes_text_frame.text)
    return "\n".join(out)


def xlsx_text(path):
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise SystemExit(f"openpyxl is needed for {path}. Install it with: {install_hint('openpyxl')}")
    CONVERTER[str(Path(path).resolve())] = "openpyxl"
    out = []
    for ws in load_workbook(str(path), read_only=True, data_only=True).worksheets:
        out.append(f"## Sheet {ws.title}")
        for row in ws.iter_rows(values_only=True):
            if any(v is not None for v in row):
                out.append("\t".join("" if v is None else str(v) for v in row))
    return "\n".join(out)


def to_text(path):
    """Plain text of a file, or None if the type can't be read as text (images, audio, unknown binaries)."""
    p = Path(path)
    ext = p.suffix.lower()
    if ext in TEXT_EXT:
        return p.read_text(encoding="utf-8", errors="ignore")
    if ext in (".docx", ".odt", ".rtf", ".epub"):
        return pandoc(p)
    if ext in (".html", ".htm"):
        return pandoc(p, "plain")
    if ext == ".pdf":
        return pdf_text(p)
    if ext == ".pptx":
        return pptx_text(p)
    if ext in (".xlsx", ".xlsm"):
        return xlsx_text(p)
    return None


NEEDS = {".docx": "pandoc", ".odt": "pandoc", ".rtf": "pandoc", ".epub": "pandoc", ".html": "pandoc", ".htm": "pandoc",
         ".pdf": "pypdf", ".pptx": "python-pptx", ".xlsx": "openpyxl", ".xlsm": "openpyxl"}


def have(tool):
    if tool == "pandoc":
        return bool(pandoc_path())
    if tool == "pypdf":
        try:
            import pypdf  # noqa: F401
            return True
        except ImportError:
            return bool(shutil.which("pdftotext"))
    mod = {"python-pptx": "pptx", "openpyxl": "openpyxl"}[tool]
    try:
        __import__(mod)
        return True
    except ImportError:
        return False


ALL_TOOLS = ["pandoc", "pypdf", "python-pptx", "openpyxl"]
PIP_NAME = {"pandoc": "pypandoc_binary", "pypdf": "pypdf", "python-pptx": "python-pptx", "openpyxl": "openpyxl"}


def cmd_doctor(paths, all_tools=False):
    """Report which converters the given files need and which are missing. Exit code 1 if a needed one is missing.
    With --all, also list the converters these files don't need, as optional, with one command to install them."""
    print(f"Python {sys.version.split()[0]}" + ("" if sys.version_info >= (3, 8) else "  (3.8 or later is needed)"))
    if all_tools and not paths:
        optional = [t for t in ALL_TOOLS if not have(t)]
        for t in ALL_TOOLS:
            print(f"{'OK     ' if t not in optional else 'not yet'} {t}")
        if optional:
            print("Optional full setup (every file type ready in advance): pip install " + " ".join(PIP_NAME[t] for t in optional))
        else:
            print("All converters are installed.")
        return
    files = []
    for a in paths:
        p = Path(a)
        files += [p] if p.is_file() else sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else []
        if not p.exists():
            print(f"Not found: {a}")
    exts = Counter(f.suffix.lower() for f in files)
    needed = {}
    for ext, n in exts.items():
        if ext in NEEDS:
            needed.setdefault(NEEDS[ext], []).append(f"{n} {ext}")
    other = sorted(e or "(no extension)" for e in exts if e not in NEEDS and e not in TEXT_EXT)
    missing = []
    for tool, what in sorted(needed.items()):
        ok = have(tool)
        print(f"{'OK     ' if ok else 'MISSING'} {tool:12} for {', '.join(what)}" + ("" if ok else f"\n        install: {install_hint(tool)}"))
        if not ok:
            missing.append(tool)
    if not needed:
        print("No converters needed: all files are plain text or Markdown.")
    if other:
        print(f"Not readable as text (cite by description, can't be quote-checked): {', '.join(other)}")
    if all_tools:
        optional = [t for t in ALL_TOOLS if t not in needed and not have(t)]
        if optional:
            print("Optional (not needed for these files): " + ", ".join(optional)
                  + "\n        full setup: pip install " + " ".join(PIP_NAME[t] for t in optional))
    if missing:
        print("Missing: " + ", ".join(missing) + ". Install them before tracing, so the conversion matches the standard method.")
        sys.exit(1)
    print("Ready.")


def relpath(path, base):
    """Path relative to base when possible, so work folders stay portable and don't record personal folders."""
    try:
        return Path(os.path.relpath(Path(path).resolve(), Path(base).resolve())).as_posix()
    except ValueError:  # different drive
        return str(Path(path).resolve())


def fp_path(fp, work):
    p = Path(fp["path"])
    return p if p.is_absolute() else (Path(work) / p).resolve()


def fingerprint(path, base=None):
    p = Path(path)
    return {
        "path": relpath(p, base) if base else str(p.resolve()),
        "modified": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="minutes"),
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest()[:16],
    }


def wc(lines):
    return sum(len(l.split()) for l in lines)


def split_large(part, words):
    """Split an oversized section at blank lines into pieces of about `words` words."""
    if wc(part) <= words * 1.5:
        return [part]
    pieces, cur = [], []
    for line in part:
        cur.append(line)
        if not line.strip() and wc(cur) >= words:
            pieces.append(cur)
            cur = []
    if cur:
        pieces.append(cur)
    return pieces


# ---------------------------------------------------------------- extract
def cmd_extract(doc, work, words=1800):
    work = Path(work)
    (work / "out").mkdir(parents=True, exist_ok=True)
    text = to_text(doc)
    if text is None:
        raise SystemExit(f"Can't read {doc} as text")
    (work / "doc.md").write_text(text, encoding="utf-8")
    lines = text.splitlines()
    # Split before each top-level heading (or second-level if there are no top-level ones),
    # break up oversized sections at paragraph boundaries, then pack small sections up to ~words per chunk.
    level = "# " if any(re.match(r"^# \S", l) for l in lines) else "## "
    starts = [i for i, l in enumerate(lines) if l.startswith(level)] or [0]
    if starts[0] != 0:
        starts = [0] + starts
    parts = [p for a, b in zip(starts, starts[1:] + [len(lines)]) for p in split_large(lines[a:b], words)]
    chunks, cur = [], []
    for part in parts:
        n = sum(len(l.split()) for l in cur)
        m = sum(len(l.split()) for l in part)
        if cur and n + m > words:
            chunks.append(cur)
            cur = []
        cur = cur + part
    if cur:
        chunks.append(cur)
    toc = ["# Chunks and headings", ""]
    for i, ch in enumerate(chunks):
        name = chr(65 + i) if i < 26 else f"Z{i}"
        (work / f"chunk_{name}.md").write_text("\n".join(ch), encoding="utf-8")
        heads = [l for l in ch if re.match(r"^#{1,3} ", l)]
        toc.append(f"## chunk_{name}.md ({sum(len(l.split()) for l in ch)} words)")
        toc += [f"- {h}" for h in heads] + [""]
    (work / "toc.md").write_text("\n".join(toc), encoding="utf-8")
    cfg_path = work / "report.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {
        "title": Path(doc).stem + ": text provenance report",
        "document": Path(doc).name,
        "doc_label": "In the target document",
        "why_label": "Why it is included",
        "evidence_label": "Strongest support",
        "evidence_rule": "",
        "scope_note": "",
        "strong_kinds": [],
        "weak_kinds": [],
        "output": str(Path(doc).resolve().with_name(Path(doc).stem + "-provenance-report.html")),
    }
    cfg["target_fingerprint"] = fingerprint(doc, work)
    cfg["target_converter"] = CONVERTER.get(str(Path(doc).resolve()), "read as text")
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print(f"{len(chunks)} chunks written to {work}; {len(text.split())} words. Edit {cfg_path} before building.")


def cmd_totext(src, dest):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    root = Path(src)
    files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
    index = dest / "INDEX.md"
    rows = index.read_text(encoding="utf-8").splitlines() if index.exists() else ["| Text copy | Original | Converter |", "|---|---|---|"]
    skipped, missing = [], []
    for f in files:
        if f.suffix.lower() in TEXT_EXT:
            continue  # already readable as is
        try:
            t = to_text(f)
        except SystemExit as e:
            missing.append(f"{f}: {e}")
            continue
        if t is None:
            skipped.append(str(f))
            continue
        rel = f.name if root.is_file() else str(f.relative_to(root))
        out = dest / (re.sub(r"[\\/:]+", "__", rel) + ".txt")
        out.write_text(t, encoding="utf-8")
        rows.append(f"| {out.name} | {relpath(f, dest)} | {CONVERTER.get(str(f.resolve()), '')} |")
        print(out, len(t.split()), "words")
    index.write_text("\n".join(dict.fromkeys(rows)) + "\n", encoding="utf-8")
    if skipped:
        print(f"Not readable as text ({len(skipped)}; images, audio or other types; cite by description): " + "; ".join(skipped[:20]))
    if missing:
        print(f"NOT CONVERTED because a converter is missing ({len(missing)}):")
        for m in missing[:20]:
            print("  " + m)
        sys.exit(1)


# ---------------------------------------------------------------- check
def norm(s):
    s = unicodedata.normalize("NFKC", str(s or ""))
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # markdown links
    s = re.sub(r"[^\w\s]|_", " ", s)  # compare words only: punctuation, table pipes and Markdown marks vary
    return re.sub(r"\s+", " ", s).strip().lower()


def fragments(excerpt):
    """Sentence-sized pieces of a quote. Tracers trim with "…" and may join list items with " / " or line breaks."""
    parts = re.split(r"…|\.\.\.|\[…\]|\s/\s|\n|(?<=[.;:!?])\s+", str(excerpt or ""))
    out = []
    for p in parts:
        n = norm(p).strip(" .;:,")
        if len(n) >= 12:
            out.append(n)
    return out


def found(excerpt, hay):
    """True if every piece is in hay, "partial" if at least half are, False otherwise, None if nothing to check."""
    fr = fragments(excerpt)
    if not fr or hay is None:
        return None
    hits = sum(1 for f in fr if f in hay)
    return True if hits == len(fr) else "partial" if hits * 2 >= len(fr) else False


def load_units(work):
    units = []
    for f in sorted(Path(work, "out").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for i, u in enumerate(d.get("units", [])):
            u["_chunk"], u["_order"], u["_file"] = d.get("chunk", f.stem), i, f
            units.append(u)
    return units


def cmd_check(work):
    work = Path(work).resolve()
    doc = norm((work / "doc.md").read_text(encoding="utf-8"))
    cfg = json.loads((work / "report.json").read_text(encoding="utf-8")) if (work / "report.json").exists() else {}
    fp = cfg.get("target_fingerprint")
    if fp and fp_path(fp, work).exists() and fingerprint(fp_path(fp, work))["sha256"] != fp["sha256"]:
        print(f"WARNING: {fp_path(fp, work)} changed after it was extracted ({fp['modified']}). "
              "Re-run extract and re-trace the changed passages, or the report will describe an old version.")
    cache, problems, per_file = {}, Counter(), {}
    required = ["id", "section", "label", "doc_excerpt", "sources", "how_added", "why_included", "verdict"]
    for u in load_units(work):
        missing = [k for k in required if k not in u]
        if missing:
            problems["missing fields"] += 1
            print(f"{u.get('id')}: missing {missing}")
        if u.get("verdict") not in VERDICTS:
            problems["bad verdict"] += 1
            print(f"{u.get('id')}: verdict {u.get('verdict')!r} not in {VERDICTS}")
        u["doc_quote_found"] = found(u["doc_excerpt"], doc)
        if u["doc_quote_found"] is False:
            problems["document quote not found"] += 1
            print(f"{u['id']}: document excerpt not found in doc.md")
        elif u["doc_quote_found"] == "partial":
            problems["document quote partly found"] += 1
        for s in u.get("sources", []):
            p = Path(s.get("file", ""))
            if not p.is_absolute():
                for base in [work, *work.parents]:
                    if (base / p).exists():
                        p = base / p
                        break
            key = str(p)
            if key not in cache:
                try:
                    t = to_text(p) if p.is_file() else None
                except SystemExit:
                    t = None
                cache[key] = norm(t) if t else None
            s["quote_found"] = found(s.get("excerpt"), cache[key]) if cache[key] else None
            if s["quote_found"] is False:
                problems["source quote not found"] += 1
                print(f"{u['id']}: quote not found in {s.get('file')}")
            elif s["quote_found"] == "partial":
                problems["source quote partly found"] += 1
        per_file.setdefault(u["_file"], []).append(u)
    ids = Counter(u["id"] for us in per_file.values() for u in us if "id" in u)
    for i, n in ids.items():
        if n > 1:
            problems["duplicate id"] += 1
            print(f"{i}: id used {n} times; ids must be unique (review notes are keyed by id)")
    for f, us in per_file.items():
        d = json.loads(f.read_text(encoding="utf-8"))
        d["units"] = [{k: v for k, v in u.items() if not k.startswith("_")} for u in sorted(us, key=lambda x: x["_order"])]
        f.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    total = sum(len(v) for v in per_file.values())
    print(f"{total} units checked. Problems: {dict(problems) or 'none'}")
    if any("quote" in k for k in problems):
        print("Quotes marked not found need a look: re-quote verbatim, or the claim may be paraphrased from memory.")


# ---------------------------------------------------------------- build
def E(s):
    return html.escape(str(s or ""))


def fmt(text):
    t = E(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t.replace("\n", "<br>")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def cmd_build(work):
    work = Path(work)
    cfg = json.loads((work / "report.json").read_text(encoding="utf-8"))
    units = load_units(work)
    if not units:
        raise SystemExit("No units in out/*.json")
    strong = {slug(k) for k in cfg.get("strong_kinds", [])}
    weak = {slug(k) for k in cfg.get("weak_kinds", [])}

    groups = OrderedDict()
    for u in sorted(units, key=lambda u: (u["_chunk"], u["_order"])):
        groups.setdefault(u.get("section", "(no section)"), []).append(u)
    vc = Counter(u.get("verdict", "Check") for u in units)
    ec = Counter(u.get("evidence", "None found") for u in units)

    def kind_cls(k):
        s = slug(k or "")
        return "k-strong" if s in strong else "k-weak" if s in weak else ""

    def qflag(v, what):
        if v is False:
            return f'<span class="qflag" title="The checker could not find this {what} verbatim">quote not found</span>'
        if v == "partial":
            return f'<span class="qflag" title="Only part of this {what} was found verbatim">quote partly found</span>'
        return ""

    def unit_html(u):
        v = u.get("verdict", "Check")
        c = VCLS.get(v, "check")
        srcs = "".join(
            f'<div class="src"><div class="srchead"><span class="kind {kind_cls(s.get("kind"))}">{E(s.get("kind"))}</span>'
            f'<code>{E(s.get("file"))}</code> <span class="loc">{E(s.get("locator"))}</span>{qflag(s.get("quote_found"), "excerpt in the source file")}</div>'
            f'<blockquote>{fmt(s.get("excerpt"))}</blockquote></div>'
            for s in u.get("sources", [])
        ) or '<p class="none">No source found.</p>'
        note = f'<div class="note"><b>Check:</b> {fmt(u["note"])}</div>' if u.get("note") else ""
        doc_ex, why = u.get("doc_excerpt", ""), u.get("why_included", "")
        return (
            f'<article class="unit v-{c}" id="u-{E(u["id"])}" data-verdict="{E(v)}">'
            f'<header><span class="uid">{E(u["id"])}</span> <span class="ulabel">{E(u.get("label"))}</span>'
            f'<span class="badge b-{c}">{E(v)}</span><span class="ev">{E(cfg.get("evidence_label", "Evidence"))}: {E(u.get("evidence"))}</span>'
            f'<button class="tog" type="button">Expand</button>'
            f'<label class="rv"><input type="checkbox" data-id="{E(u["id"])}"> Reviewed</label></header>'
            f'<div class="cols"><div class="col doc"><h4>{E(cfg.get("doc_label", "In the document"))}{qflag(u.get("doc_quote_found"), "text in the document")}</h4>'
            f'<blockquote class="s-doc">{fmt(doc_ex)}</blockquote></div>'
            f'<div class="col s-src"><h4>Source(s)</h4>{srcs}</div></div>'
            f'<div class="meta s-meta"><p><b>How it was added:</b> {fmt(u.get("how_added"))}</p>'
            f'<p><b>{E(cfg.get("why_label", "Why it is included"))}:</b> {fmt(why)}</p>{note}</div>'
            f'<textarea data-id="{E(u["id"])}" placeholder="Your review note (saved in this browser)"></textarea></article>'
        )

    body = "".join(
        f'<section id="s-{i}"><h2>{E(s)}</h2>' + "".join(unit_html(u) for u in us) + "</section>"
        for i, (s, us) in enumerate(groups.items())
    )
    issues = sorted(
        (u for u in units if u.get("verdict") in ("Overstates", "Unsupported", "Check")),
        key=lambda u: (-VERDICTS.index(u["verdict"]), u["_chunk"], u["_order"]),
    )
    issue_rows = "".join(
        f'<tr data-id="{E(u["id"])}"><td><a href="#u-{E(u["id"])}">{E(u["id"])}</a></td><td><span class="badge b-{VCLS[u["verdict"]]}">{E(u["verdict"])}</span></td>'
        f'<td>{E(u.get("label"))}</td><td>{fmt(u.get("note"))}</td></tr>'
        for u in issues
    )
    flags = [u.get("doc_quote_found") for u in units] + [s.get("quote_found") for u in units for s in u.get("sources", [])]
    qmiss, qpart, qok = flags.count(False), flags.count("partial"), flags.count(True)
    checked = any("doc_quote_found" in u for u in units)
    qline = (f"<p><b>Quote check.</b> All {qok} checkable excerpts were found verbatim in their files. "
             f"Images, recordings and other non-text sources can't be checked.</p>"
             if checked and not (qmiss or qpart) else
             f"<p><b>Quote check.</b> {qok} excerpts were found verbatim in their file. {qpart} were only partly found and "
             f"{qmiss} not found; these are tagged <span class=\"qflag\">quote partly found</span> or <span class=\"qflag\">quote not found</span>. "
             f"Images, recordings and other non-text sources can't be checked.</p>"
             if checked else "<p><b>Quote check.</b> Not run (run <code>prov.py check</code> before building).</p>")
    vchips = "".join(f'<button class="chip b-{VCLS[v]}" data-f="{v}">{v} <b>{vc.get(v, 0)}</b></button>' for v in VERDICTS)
    erows = "".join(f"<tr><td>{E(k)}</td><td>{n}</td></tr>" for k, n in ec.most_common())
    rule = f'<p><b>Source rules.</b> {fmt(cfg["evidence_rule"])}</p>' if cfg.get("evidence_rule") else ""
    fp = cfg.get("target_fingerprint")
    if fp:
        changed = fp_path(fp, work).exists() and fingerprint(fp_path(fp, work))["sha256"] != fp["sha256"]
        rule += (f'<p><b>Traced version.</b> <code>{E(Path(fp["path"]).name)}</code> as of {E(fp["modified"])} '
                 f'(SHA-256 {E(fp["sha256"])}).' + (' <span class="qflag">The file has changed since; this report may be out of date.</span>' if changed else "") + "</p>")
    idx = work / "srctxt" / "INDEX.md"
    fallback_srcs = [l for l in idx.read_text(encoding="utf-8").splitlines() if "built-in fallback" in l] if idx.exists() else []
    if cfg.get("target_converter") == "built-in fallback" or fallback_srcs:
        what = (["the target"] if cfg.get("target_converter") == "built-in fallback" else []) + (
            [f"{len(fallback_srcs)} source(s)"] if fallback_srcs else [])
        verb = "was" if what == ["the target"] or what == ["1 source(s)"] else "were"
        rule += (f'<p><span class="qflag">Lower-fidelity conversion</span> pandoc was not available, so {" and ".join(what)} '
                 f"{verb} converted with the built-in reader. Tables, lists and formatting may be simplified, "
                 "and some quote checks may miss.</p>")

    page = TEMPLATE
    for k, v in {
        "%%TITLE%%": E(cfg.get("title", "Text provenance report")),
        "%%DOC%%": E(cfg.get("document", "")),
        "%%SCOPE%%": E(cfg.get("scope_note", "")),
        "%%DATE%%": date.today().isoformat(),
        "%%NUNITS%%": str(len(units)),
        "%%NSECT%%": str(len(groups)),
        "%%RULE%%": rule,
        "%%QLINE%%": qline,
        "%%VCHIPS%%": vchips,
        "%%NISSUES%%": str(len(issues)),
        "%%ISSUES%%": issue_rows,
        "%%EROWS%%": erows,
        "%%EVLABEL%%": E(cfg.get("evidence_label", "Evidence")),
        "%%BODY%%": body,
        "%%KEY%%": "prov-" + slug(cfg.get("title", "report"))[:60],
    }.items():
        page = page.replace(k, v)
    out = Path(cfg.get("output") or work / "provenance-report.html")
    if not out.is_absolute():
        out = work / out
    out.write_text(page, encoding="utf-8")
    print(out, len(units), "units", dict(vc))


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%%TITLE%%</title><style>
:root{--navy:#14213d;--vio:#5b3fd0;--bg:#f6f7fb;--line:#dde1ea;--ok:#1f8a4c;--drift:#b7791f;--over:#c2410c;--unsup:#b91c1c;--check:#6d28d9}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 "Segoe UI",system-ui,sans-serif;color:#1d2433;background:var(--bg)}
.top{background:var(--navy);color:#fff;padding:12px 24px;position:sticky;top:0;z-index:5}
.top h1{font-size:17px;margin:0 0 8px}.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-size:13px}
.bar input[type=search]{padding:6px 10px;border-radius:6px;border:0;width:280px}.bar select{padding:5px;border-radius:6px;border:0}
.bar button{border:0;border-radius:6px;padding:5px 10px;cursor:pointer}#hits{font-weight:600;color:#c7d2fe}#prog{margin-left:auto}
main{padding:20px 28px;max-width:1400px;margin:0 auto}h2{color:var(--navy);border-bottom:2px solid var(--vio);padding-bottom:4px;margin-top:34px}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px 20px;margin-bottom:16px}
body.searching .intro{display:none}
.unit{background:#fff;border:1px solid var(--line);border-left:5px solid var(--ok);border-radius:8px;margin:14px 0;padding:12px 16px}
.v-drift{border-left-color:var(--drift)}.v-over{border-left-color:var(--over)}.v-unsup{border-left-color:var(--unsup)}.v-check{border-left-color:var(--check)}
.unit header{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.uid{font-weight:700;color:var(--vio)}.ulabel{font-weight:600;flex:1}
.badge{color:#fff;border-radius:10px;padding:1px 9px;font-size:12px}.b-ok{background:var(--ok)}.b-drift{background:var(--drift)}.b-over{background:var(--over)}.b-unsup{background:var(--unsup)}.b-check{background:var(--check)}
.ev{font-size:12px;color:#555}.rv{font-size:12px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:10px}.col h4{margin:0 0 6px;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#666}
blockquote{margin:0 0 8px;padding:8px 12px;background:#f3f4f8;border-radius:6px;font-size:13px}.doc blockquote{background:#eef0ff}
.srchead{font-size:12px;margin-bottom:3px;word-break:break-all}.loc{color:#666}code{font-size:11.5px;color:#334}
.kind{background:#e5e7eb;border-radius:4px;padding:0 6px;font-weight:600;margin-right:4px}.k-strong{background:#d1fae5}.k-weak{background:#fee2e2}
.qflag{background:#fef3c7;color:#92400e;border-radius:4px;padding:0 5px;margin-left:6px;font-size:11px;text-transform:none;letter-spacing:0}
.meta p{margin:6px 0}.note{background:#fff7ed;border:1px solid #fed7aa;border-radius:6px;padding:6px 10px;margin:6px 0}
textarea{width:100%;min-height:34px;border:1px solid var(--line);border-radius:6px;padding:6px;font:inherit;font-size:12.5px}
.chip{border:0;border-radius:14px;padding:4px 12px;margin:2px;color:#fff;cursor:pointer}.chip.off{opacity:.3}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{border:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}th{background:#eef0f6}
mark{background:#fde047;padding:0 1px;border-radius:2px}
.hidden{display:none}.none{color:var(--unsup)}
.unit.done{padding:6px 16px;background:#f7f9f8}.unit.done .ulabel::before{content:"\2713  ";color:var(--ok)}
body:not(.searching) .unit.done:not(.open) .cols,body:not(.searching) .unit.done:not(.open) .meta,body:not(.searching) .unit.done:not(.open) textarea{display:none}
.tog{display:none;border:1px solid var(--line);background:#fff;border-radius:6px;padding:1px 8px;font-size:12px;color:var(--vio);cursor:pointer}
body:not(.searching) .unit.done .tog{display:inline-block}
tr.done td{opacity:.45}tr.done td:first-child::after{content:" \2713";color:var(--ok)}
@media (max-width:1000px){.cols{grid-template-columns:1fr}}
@media print{.top .bar,textarea,.chip{display:none}.top{position:static}}
</style></head><body>
<div class="top"><h1>%%TITLE%%</h1>
<div class="bar"><input type="search" id="q" placeholder="Find a term" aria-label="Search term">
<select id="scope" aria-label="Search in"><option value="doc">in document text</option><option value="src">in source excerpts</option><option value="meta">in how/why, checks and my notes</option><option value="all">everywhere</option></select>
<label><input type="checkbox" id="word"> Whole word</label><button id="clr">Clear</button><label title="Hide the units you have marked Reviewed"><input type="checkbox" id="hiderev"> Hide reviewed</label><span id="hits"></span><span id="prog"></span></div></div>
<main>
<div class="card intro"><p><b>What this is.</b> Each passage of <code>%%DOC%%</code> is shown next to verbatim excerpt(s) from the source it came from, with how it got into the target document and why it is included. Text is grouped into one unit only where it came from the same source(s). %%SCOPE%% Generated %%DATE%%; %%NUNITS%% units across %%NSECT%% sections.</p>
%%RULE%%
<p><b>Verdicts.</b> Verified = the text matches its source, and the source is one the rules accept as support. Minor drift = small wording or emphasis difference. Overstates = the target claims more than the source. Unsupported = no source found. Check = sources conflict or could not be confirmed. Verdicts are machine-assisted; your Reviewed ticks and notes are saved in this browser only, so use Export to keep them.</p>
<p><b>Reviewing.</b> Ticking <b>Reviewed</b> collapses a unit to a single row. Select <b>Expand</b> to look at it again, or turn on <b>Hide reviewed</b> at the top to hide reviewed units, so that only the work left is on screen.</p>
%%QLINE%%
<p><b>Search.</b> Type a term to show only the passages that contain it, with the term highlighted. Choose where to look: the document text (to see every passage that uses a term and where each came from), the source excerpts, or the how/why notes and your own notes.</p>
<div>%%VCHIPS%% <button class="chip" style="background:#475569" data-f="*">Show all</button> <button class="chip" style="background:#0f766e" id="exp">Export review notes</button> <button class="chip" style="background:#0f766e" id="imp">Import review notes</button><input type="file" id="impf" accept=".json" class="hidden"></div></div>
<div class="card intro"><h3 style="margin-top:0">Items to look at first (%%NISSUES%%)</h3><table><tr><th>Unit</th><th>Verdict</th><th>Text</th><th>Why</th></tr>%%ISSUES%%</table>
<h3>Strongest %%EVLABEL%% per unit</h3><table style="width:auto"><tr><th>%%EVLABEL%%</th><th>Units</th></tr>%%EROWS%%</table></div>
%%BODY%%</main>
<script>
const K='%%KEY%%',ALL=['Verified','Minor drift','Overstates','Unsupported','Check'];
let st={};try{st=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
const save=()=>{try{localStorage.setItem(K,JSON.stringify(st))}catch(e){}};
const rec=id=>(st[id]=st[id]||{});
const UK=K+'-ui';let ui={};try{ui=JSON.parse(localStorage.getItem(UK)||'{}')}catch(e){}
const saveUi=()=>{try{localStorage.setItem(UK,JSON.stringify(ui))}catch(e){}};
function setDone(c){const u=c.closest('.unit');u.classList.toggle('done',c.checked);u.classList.remove('open');u.querySelector('.tog').textContent='Expand';
 document.querySelectorAll('tr[data-id]').forEach(r=>{if(r.dataset.id===c.dataset.id)r.classList.toggle('done',c.checked)})}
function bindState(){
 document.querySelectorAll('.rv input').forEach(c=>{c.checked=!!(st[c.dataset.id]||{}).done;setDone(c);
  c.onchange=()=>{rec(c.dataset.id).done=c.checked;setDone(c);save();prog();if(ui.hideRev)apply()}});
 document.querySelectorAll('textarea').forEach(t=>{t.value=(st[t.dataset.id]||{}).note||'';t.oninput=()=>{rec(t.dataset.id).note=t.value;save()}});prog()}
function prog(){const a=document.querySelectorAll('.rv input'),d=[...a].filter(x=>x.checked).length;document.getElementById('prog').textContent=d+' / '+a.length+' reviewed'}
let on=new Set(ALL);
const SC={doc:['.s-doc'],src:['.s-src'],meta:['.s-meta','textarea'],all:['.s-doc','.s-src','.s-meta','textarea','.uid','.ulabel']};
const orig=new Map();
function restore(){orig.forEach((h,el)=>{el.innerHTML=h});orig.clear()}
function mark(el,re){if(el.tagName==='TEXTAREA')return;if(!orig.has(el))orig.set(el,el.innerHTML);
 const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT),ns=[];while(w.nextNode())ns.push(w.currentNode);
 ns.forEach(n=>{const t=n.nodeValue;re.lastIndex=0;if(!re.test(t))return;re.lastIndex=0;const f=document.createDocumentFragment();let i=0,m;
  while((m=re.exec(t))){f.append(t.slice(i,m.index));const k=document.createElement('mark');k.textContent=m[0];f.append(k);i=m.index+m[0].length;if(!m[0].length)re.lastIndex++}
  f.append(t.slice(i));n.replaceWith(f)})}
function textOf(el){return el.tagName==='TEXTAREA'?el.value:el.textContent}
function apply(){restore();const q=document.getElementById('q').value.trim(),scope=document.getElementById('scope').value,ww=document.getElementById('word').checked;
 let re=null;if(q){const esc=q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&').replace(/\s+/g,'\\s+');re=new RegExp(ww?'\\b'+esc+'\\b':esc,'gi')}
 document.body.classList.toggle('searching',!!re);let units=0,occ=0;
 document.querySelectorAll('.unit').forEach(u=>{let hit=!re;if(re){const els=SC[scope].flatMap(s=>[...u.querySelectorAll(s)]);
   els.forEach(el=>{const c=(textOf(el).match(re)||[]).length;if(c){hit=true;occ+=c;mark(el,re)}})}
  const show=hit&&on.has(u.dataset.verdict)&&!(ui.hideRev&&u.classList.contains('done'));u.classList.toggle('hidden',!show);if(show&&re)units++});
 let secs=0;document.querySelectorAll('main section').forEach(s=>{const v=!!s.querySelector('.unit:not(.hidden)');s.classList.toggle('hidden',!v);if(v)secs++});
 document.getElementById('hits').textContent=re?(units?`${occ} match${occ==1?'':'es'} in ${units} passage${units==1?'':'s'} across ${secs} section${secs==1?'':'s'}`:'No matches'):'';
 if(re)window.scrollTo(0,0)}
let tm;const later=()=>{clearTimeout(tm);tm=setTimeout(apply,200)};
document.getElementById('q').addEventListener('input',later);
document.getElementById('q').addEventListener('keydown',e=>{if(e.key==='Escape'){e.target.value='';apply()}});
document.getElementById('scope').onchange=apply;document.getElementById('word').onchange=apply;
document.getElementById('clr').onclick=()=>{document.getElementById('q').value='';apply()};
document.querySelectorAll('.chip[data-f]').forEach(b=>b.onclick=()=>{const f=b.dataset.f;
 if(f==='*')on=new Set(ALL);else if(on.size===ALL.length)on=new Set([f]);else{on.has(f)?on.delete(f):on.add(f);if(!on.size)on=new Set(ALL)}
 document.querySelectorAll('.chip[data-f]').forEach(x=>x.classList.toggle('off',x.dataset.f!=='*'&&!on.has(x.dataset.f)));apply()});
document.getElementById('exp').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(st,null,2)],{type:'application/json'}));a.download=K+'-review-notes.json';a.click()};
document.getElementById('imp').onclick=()=>document.getElementById('impf').click();
document.getElementById('impf').onchange=e=>{const f=e.target.files[0];if(!f)return;f.text().then(t=>{const d=JSON.parse(t);Object.entries(d).forEach(([k,v])=>{st[k]=Object.assign(rec(k),v)});save();bindState()})};
document.querySelectorAll('.tog').forEach(b=>b.onclick=()=>{const u=b.closest('.unit');b.textContent=u.classList.toggle('open')?'Collapse':'Expand'});
const hr=document.getElementById('hiderev');hr.checked=!!ui.hideRev;hr.onchange=()=>{ui.hideRev=hr.checked;saveUi();apply()};
document.querySelectorAll('tr[data-id] a').forEach(a=>a.addEventListener('click',()=>{const u=document.getElementById('u-'+a.closest('tr').dataset.id);
 if(u&&u.classList.contains('hidden')&&ui.hideRev){hr.checked=false;ui.hideRev=false;saveUi();apply()}}));
bindState();if(ui.hideRev)apply();
</script></body></html>"""


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--fallback" in a:
        a.remove("--fallback")
        ALLOW_FALLBACK = True
    w = 1800
    if "--words" in a:
        i = a.index("--words")
        w = int(a[i + 1])
        del a[i:i + 2]
    if not a:
        print(__doc__)
        sys.exit(1)
    if a[0] == "doctor":
        all_tools = "--all" in a
        rest = [x for x in a[1:] if x != "--all"]
        if not rest and not all_tools:
            print(__doc__)
            sys.exit(1)
        cmd_doctor(rest, all_tools)
    elif a[0] == "extract" and len(a) == 3:
        cmd_extract(a[1], a[2], w)
    elif a[0] == "totext" and len(a) == 3:
        cmd_totext(a[1], a[2])
    elif a[0] == "check" and len(a) == 2:
        cmd_check(a[1])
    elif a[0] == "build" and len(a) == 2:
        cmd_build(a[1])
    else:
        print(__doc__)
        sys.exit(1)
