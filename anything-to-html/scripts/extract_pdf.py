"""Extract a PDF into Markdown plus image files, ready for pandoc or for
writing the HTML fragment directly.

Usage:
    python extract_pdf.py IN.pdf --out WORK_DIR [--ocr auto|tesseract|windows|macos|none]
                          [--dpi 200] [--min-image 40] [--render]

Writes to WORK_DIR:
    raw.md               headings (by font size), paragraphs, bullet lists,
                         tables (Markdown), image links, <!-- page N --> markers
    media/pNN-iK.<ext>   every image, in reading order
    pages/pNN.png        page renders, only with --render (to look at layouts)
    extract-report.json  pages, scanned pages, images, tables, dropped
                         header/footer lines, heading sizes used

Needs PyMuPDF (`pip install pymupdf`). Without it, falls back to pypdf or
pdftotext and writes plain text only (no headings, images or tables) and says so.

Scanned pages (no text layer) are OCR'd when --ocr is on:
    auto       tesseract if installed, else the OS engine (Windows or macOS),
               else the page is marked and skipped
    tesseract  PyMuPDF's OCR (needs tesseract on PATH; tessdata is located
               automatically or via TESSDATA_PREFIX). Windows, macOS, Linux.
    windows    Windows 10/11 built-in engine via ocr_windows.ps1 (no install)
    macos      Apple Vision via ocr_macos.swift (needs Xcode Command Line Tools)
The extractor never installs anything. Works on Windows, macOS and Linux.
"""
import argparse
import collections
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BULLET = re.compile(r'^\s*([•●▪■◦○\-–—*]|o(?=\s))\s+')
NUMBERED = re.compile(r'^\s*(\d{1,3}[.)]|[a-z][.)]|[ivx]{1,5}[.)])\s+', re.I)


def norm_line(s):
    return re.sub(r'\d+', '#', re.sub(r'\s+', ' ', s)).strip().lower()


def md_escape_cell(s):
    return s.replace('|', '\\|').replace('\n', ' ').strip()


# ── Fallbacks when PyMuPDF is missing ────────────────────────────────────────

def fallback(pdf, out):
    text, how = None, None
    try:
        from pypdf import PdfReader
        r = PdfReader(str(pdf))
        text = '\n\n'.join(f'<!-- page {i + 1} -->\n\n' + (p.extract_text() or '') for i, p in enumerate(r.pages))
        how = 'pypdf'
    except Exception:
        pass
    if text is None and shutil.which('pdftotext'):
        r = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
        text, how = r.stdout, 'pdftotext -layout'
    if text is None:
        sys.exit('PyMuPDF is not installed and neither pypdf nor pdftotext is available. '
                 'Ask the user before installing: python -m pip install pymupdf')
    (out / 'raw.md').write_text(text, encoding='utf-8')
    (out / 'extract-report.json').write_text(json.dumps({'method': how, 'note': 'plain text only: no headings, images or tables'}, indent=2), encoding='utf-8')
    print(f'PyMuPDF not installed; wrote plain text with {how} to {out / "raw.md"}. '
          f'Headings, images and tables must be rebuilt by hand. For structure, ask the user before installing: python -m pip install pymupdf')


# ── OCR ──────────────────────────────────────────────────────────────────────

def ocr_mode(requested):
    if requested == 'none':
        return None
    has_tess = shutil.which('tesseract') is not None
    is_win = platform.system() == 'Windows' and shutil.which('powershell') is not None
    is_mac = platform.system() == 'Darwin' and shutil.which('swift') is not None
    if requested == 'tesseract':
        return 'tesseract' if has_tess else None
    if requested == 'windows':
        return 'windows' if is_win else None
    if requested == 'macos':
        return 'macos' if is_mac else None
    return 'tesseract' if has_tess else ('windows' if is_win else ('macos' if is_mac else None))


def find_tessdata():
    """Folder with eng.traineddata, or None to let PyMuPDF look for it."""
    import os
    cands = [os.environ.get('TESSDATA_PREFIX')]
    exe = shutil.which('tesseract')
    if exe:
        cands.append(str(Path(exe).resolve().parent / 'tessdata'))           # Windows (UB-Mannheim build)
    cands += ['/opt/homebrew/share/tessdata', '/usr/local/share/tessdata',    # macOS (Homebrew)
              '/usr/share/tesseract-ocr/5/tessdata', '/usr/share/tesseract-ocr/4.00/tessdata', '/usr/share/tessdata']  # Linux
    for c in cands:
        if c and (Path(c) / 'eng.traineddata').is_file():
            return c
    return None


def ocr_external(png_paths, mode):
    """OCR with the OS engine: PowerShell script on Windows, Swift script on macOS."""
    if mode == 'windows':
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(HERE / 'ocr_windows.ps1')]
    else:
        cmd = ['swift', str(HERE / 'ocr_macos.swift')]
    r = subprocess.run(cmd + [str(p) for p in png_paths], capture_output=True, text=True, encoding='utf-8', errors='replace',
                       timeout=120 * max(1, len(png_paths)))
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f'{mode} OCR failed')
    texts, cur = {}, None
    for line in r.stdout.splitlines():
        if line.startswith('===== '):
            cur = line[6:].strip()
            texts[cur] = []
        elif cur is not None:
            texts[cur].append(line)
    return {k: '\n'.join(v).strip() for k, v in texts.items()}


# ── Main extraction ──────────────────────────────────────────────────────────

def extract(args):
    import pymupdf
    pdf, out = Path(args.input), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    media = out / 'media'
    media.mkdir(exist_ok=True)
    doc = pymupdf.open(str(pdf))
    n = doc.page_count

    # Pass 1: font statistics and repeated header/footer lines.
    size_chars = collections.Counter()
    edge_lines = collections.Counter()
    page_data = []
    for pno, page in enumerate(doc):
        d = page.get_text('dict')
        blocks = d['blocks']
        text_lines = []
        for b in blocks:
            if b['type'] != 0:
                continue
            for l in b['lines']:
                t = ''.join(s['text'] for s in l['spans']).strip()
                if not t:
                    continue
                for s in l['spans']:
                    if s['text'].strip():
                        size_chars[round(s['size'] * 2) / 2] += len(s['text'].strip())
                text_lines.append((l['bbox'][1], t))
        text_lines.sort()
        h = page.rect.height
        for y, t in text_lines:
            if y < h * 0.08 or y > h * 0.9:
                edge_lines[norm_line(t)] += 1
        page_data.append((page, blocks, bool(text_lines)))

    body = size_chars.most_common(1)[0][0] if size_chars else 10.0
    heading_sizes = sorted({s for s in size_chars if s >= body * 1.12 and size_chars[s] >= 3}, reverse=True)
    levels = {s: min(i + 1, 4) for i, s in enumerate(heading_sizes)}  # largest = h1
    repeat_min = max(3, int(n * 0.4)) if n >= 4 else n + 1
    repeated = {t for t, c in edge_lines.items() if c >= repeat_min and t}

    # Pass 2: write Markdown.
    md, report = [], {'file': pdf.name, 'pages': n, 'text_pages': 0, 'scanned_pages': [], 'ocr': None, 'images': 0,
                      'tables': 0, 'body_font_size': body, 'heading_font_sizes': {str(s): f'h{l}' for s, l in levels.items()},
                      'dropped_repeated_lines': sorted(repeated), 'notes': []}
    seen_images = {}
    scanned_pngs = []
    mode = ocr_mode(args.ocr)
    if args.render:
        (out / 'pages').mkdir(exist_ok=True)

    for pno, (page, blocks, has_text) in enumerate(page_data):
        pn = pno + 1
        md.append(f'<!-- page {pn} -->\n')
        if args.render:
            page.get_pixmap(dpi=100).save(str(out / 'pages' / f'p{pn:02d}.png'))

        if not has_text:
            report['scanned_pages'].append(pn)
            png = out / 'media' / f'p{pn:02d}-scan.png'
            page.get_pixmap(dpi=args.dpi).save(str(png))
            if mode == 'tesseract':
                try:
                    tp = page.get_textpage_ocr(dpi=args.dpi, full=True, tessdata=find_tessdata())
                    md.append(page.get_text(textpage=tp).strip() + '\n')
                    report['ocr'] = 'tesseract'
                except Exception as e:  # noqa: BLE001
                    md.append(f'<!-- page {pn}: scanned, OCR failed: {e} -->\n')
                    report['notes'].append(f'page {pn}: tesseract OCR failed: {e}')
            elif mode in ('windows', 'macos'):
                scanned_pngs.append((len(md), png))
                md.append('')  # placeholder, filled after OCR
            else:
                md.append(f'<!-- page {pn}: scanned image, no text layer; OCR not available -->\n')
            md.append(f'![Page {pn} (scanned)](media/{png.name})\n')
            continue

        report['text_pages'] += 1
        tables = []
        try:
            tf = page.find_tables()
            for t in tf.tables:
                if t.row_count >= 2 and t.col_count >= 2:
                    tables.append((pymupdf.Rect(t.bbox), t))
        except Exception as e:  # noqa: BLE001
            report['notes'].append(f'page {pn}: table detection failed: {e}')
        emitted_tables = set()

        for b in sorted(blocks, key=lambda b: (round(b['bbox'][1]), b['bbox'][0])):
            bb = pymupdf.Rect(b['bbox'])

            if b['type'] == 1:  # image block
                w, h = b.get('width', 0), b.get('height', 0)
                if w < args.min_image or h < args.min_image:
                    continue
                data = b['image']
                digest = hashlib.md5(data).hexdigest()
                if digest not in seen_images:
                    ext = b.get('ext', 'png')
                    name = f'p{pn:02d}-i{len(seen_images) + 1}.{ext}'
                    (media / name).write_bytes(data)
                    seen_images[digest] = name
                    report['images'] += 1
                md.append(f'![](media/{seen_images[digest]})\n')
                continue

            # Text block inside a table: emit the table once, skip the text.
            hit = next((i for i, (r, _) in enumerate(tables) if r.intersects(bb) and (r & bb).get_area() > bb.get_area() * 0.5), None)
            if hit is not None:
                if hit not in emitted_tables:
                    emitted_tables.add(hit)
                    rows = tables[hit][1].extract()
                    rows = [[md_escape_cell(c or '') for c in r] for r in rows]
                    if rows:
                        md.append('| ' + ' | '.join(rows[0]) + ' |')
                        md.append('|' + '---|' * len(rows[0]))
                        for r in rows[1:]:
                            md.append('| ' + ' | '.join(r) + ' |')
                        md.append('')
                        report['tables'] += 1
                continue

            lines = []
            for l in b['lines']:
                spans = [s for s in l['spans'] if s['text'].strip()]
                if not spans:
                    continue
                text = ''.join(s['text'] for s in l['spans']).strip()
                size = round(max(s['size'] for s in spans) * 2) / 2
                bold = all(s['flags'] & 16 for s in spans)
                lines.append((text, size, bold))
            if not lines:
                continue
            if all(norm_line(t) in repeated for t, _, _ in lines):
                continue
            if all(re.fullmatch(r'(page\s*)?\d+(\s*(of|/)\s*\d+)?', t.strip(), re.I) for t, _, _ in lines):
                continue  # page number

            top_size = max(s for _, s, _ in lines)
            if top_size in levels and sum(len(t) for t, _, _ in lines) < 200:
                md.append('#' * levels[top_size] + ' ' + ' '.join(t for t, _, _ in lines) + '\n')
                continue

            if all(BULLET.match(t) or NUMBERED.match(t) for t, _, _ in lines):
                for t, _, _ in lines:
                    if BULLET.match(t):
                        md.append('- ' + BULLET.sub('', t))
                    else:
                        md.append(t)
                md.append('')
                continue

            para, buf = [], ''
            for t, _, _ in lines:
                if BULLET.match(t) and buf:
                    para.append(buf)
                    buf = ''
                if buf.endswith('-') and t[:1].islower():
                    buf = buf[:-1] + t
                else:
                    buf = (buf + ' ' + t).strip()
            para.append(buf)
            text = ' '.join(para)
            if all(bl for _, _, bl in lines) and len(text) < 120 and not text.endswith('.'):
                text = f'**{text}**'
            md.append(text + '\n')

    if scanned_pngs:
        try:
            texts = ocr_external([p for _, p in scanned_pngs], mode)
            for idx, png in scanned_pngs:
                md[idx] = texts.get(str(png), '').strip() + '\n'
            report['ocr'] = mode
        except Exception as e:  # noqa: BLE001
            for idx, png in scanned_pngs:
                md[idx] = f'<!-- scanned page; {mode} OCR failed: {e} -->\n'
            report['notes'].append(f'{mode} OCR failed: {e}')

    (out / 'raw.md').write_text('\n'.join(md), encoding='utf-8')
    (out / 'extract-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    sc = report['scanned_pages']
    print(f'Wrote {out / "raw.md"}: {n} pages, {report["text_pages"]} with text, {len(sc)} scanned'
          + (f' (OCR: {report["ocr"] or "not available"})' if sc else '')
          + f', {report["images"]} images, {report["tables"]} tables, headings from font sizes {list(levels)} (body {body})')
    if report['dropped_repeated_lines']:
        print('Dropped repeated header/footer lines: ' + '; '.join(report['dropped_repeated_lines'][:6]))
    for note in report['notes']:
        print('NOTE: ' + note)
    if sc and not report['ocr']:
        print('Scanned pages were saved as images only. OCR options: tesseract (any OS), the Windows built-in engine '
              '(--ocr windows), or Apple Vision on macOS (--ocr macos, needs Xcode Command Line Tools).')


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input')
    ap.add_argument('--out', required=True)
    ap.add_argument('--ocr', choices=['auto', 'tesseract', 'windows', 'macos', 'none'], default='auto')
    ap.add_argument('--dpi', type=int, default=200, help='render resolution for scanned pages')
    ap.add_argument('--min-image', type=int, default=40, help='skip images smaller than this (px)')
    ap.add_argument('--render', action='store_true', help='also render every page to pages/pNN.png')
    args = ap.parse_args()
    try:
        import pymupdf  # noqa: F401
    except ImportError:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        fallback(Path(args.input), out)
        return
    extract(args)


if __name__ == '__main__':
    main()
