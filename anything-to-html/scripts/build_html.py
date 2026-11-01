"""Build HTML documentation from content fragments and the template.

The template (assets/html-doc-template.html) owns ALL styling and behaviour.
You write only the content that goes inside <main>, using the template's
component classes; this script wraps it in the template's exact CSS, JS,
header, sidebar and footer, so the look cannot drift.

Usage:
    # One self-contained file (sidebar = chapters, images embedded)
    python build_html.py single CONTENT.html --out OUT.html --product NAME
                         [--title "Page title"] [--header-title "Header text"]
                         [--year 2026] [--no-embed]

    # Multi-page web help site (one page per topic, shared sidebar)
    python build_html.py site NAV.json --src SRC_DIR --out OUT_DIR

CONTENT.html / SRC_DIR/<file>.html are fragments: only the inner content of
<main> (cover, sections, ...), no <html>, <head>, <body>, <style> or <script>.

Single mode:  every <h2> becomes a sidebar chapter and every <h3> under it a
              child link. Missing heading ids are added. Pick a chapter icon
              with <h2 data-icon="tool">. Relative <img src> files are embedded
              as base64 unless --no-embed is given.
Site mode:    see references/site-mode.md for the NAV.json format. Missing hub
              pages are generated from NAV.json; breadcrumbs and Previous/Next
              buttons are added; images are copied to OUT_DIR/images/;
              help-map.json is written for pages that have an appRoute.

Standard library only.
"""
import argparse
import base64
import datetime
import hashlib
import html
import json
import mimetypes
import re
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / 'assets' / 'html-doc-template.html'

ICONS = {
    'home': '<path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    'user': '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    'users': '<circle cx="9" cy="8" r="3"/><path d="M3 19a6 6 0 0 1 12 0"/><path d="M17 12l2 2 4-4"/>',
    'tool': '<path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>',
    'book': '<path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/>',
    'clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    'download': '<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    'plus': '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>',
    'bolt': '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    'chat': '<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>',
    'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    'check': '<path d="M9 4h6"/><path d="M8 4a2 2 0 0 0-2 2v1H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4"/><path d="M8 13l2 2 4-4"/>',
    'chart': '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    'trend': '<path d="M4 19h16"/><path d="M6 15l4-4 3 3 5-6"/>',
    'send': '<path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/>',
    'settings': '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1z"/>',
    'file': '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>',
}
CHEVRON = '<path d="M9 18l6-6-6-6"/>'
ARROW = '<path d="M5 12h14M12 5l7 7-7 7"/>'

HEADING = re.compile(r'<h([23])((?:\s[^>]*)?)>(.*?)</h\1>', re.S | re.I)
IMG_SRC = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', re.I)

warnings = []


def esc(s):
    return html.escape(s, quote=True)


def text_of(fragment):
    return html.unescape(re.sub(r'<[^>]+>', '', fragment)).strip()


def svg(name, size, stroke):
    inner = ICONS.get(name)
    if inner is None:
        warnings.append(f'unknown icon "{name}", using "file" (choose from: {", ".join(sorted(ICONS))})')
        inner = ICONS['file']
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>')


def slugify(text, used):
    base = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-') or 'section'
    slug, n = base, 2
    while slug in used:
        slug, n = f'{base}-{n}', n + 1
    used.add(slug)
    return slug


# ── Sidebar ──────────────────────────────────────────────────────────────────

def sidebar_html(home, sections, current=None, open_first=False):
    """home: (label, href) or None. sections: [{label, href, icon, children: [(label, href)]}]."""
    out = []
    if home:
        cls = 'sb-home active' if current == home[1] else 'sb-home'
        out.append(f'<a class="{cls}" href="{esc(home[1])}">{svg("home", 14, 2)}<span>{esc(home[0])}</span></a>')
        out.append('<div class="sb-divider"></div>')
    for i, s in enumerate(sections):
        kids = s.get('children', [])
        active = current is not None and (current == s['href'] or current in [k[1] for k in kids])
        is_open = active or (open_first and i == 0)
        chevron = (f'<span class="nav-chevron" aria-hidden="true">{svg_raw(CHEVRON, 12, 2.5)}</span>' if kids else '')
        out.append(f'<div class="nav-section{" open" if is_open else ""}">')
        out.append(f'  <div class="nav-sec-hd{" sec-active" if active else ""}">')
        out.append(f'    <a class="nav-sec-link" href="{esc(s["href"])}"><span class="nav-sec-icon">{svg(s.get("icon") or "file", 16, 1.8)}</span>'
                   f'<span class="nav-sec-lbl">{esc(s["label"])}</span></a>')
        out.append(f'    {chevron}')
        out.append('  </div>')
        if kids:
            out.append('  <ul class="nav-children">')
            for label, href in kids:
                cls = ' class="active"' if current == href else ''
                out.append(f'    <li><a href="{esc(href)}"{cls}>{esc(label)}</a></li>')
            out.append('  </ul>')
        out.append('</div>')
    return '\n        '.join(out)


def svg_raw(inner, size, stroke):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')


# ── Template filling ─────────────────────────────────────────────────────────

def load_template():
    if not TEMPLATE.exists():
        sys.exit(f'Template not found: {TEMPLATE}')
    t = TEMPLATE.read_text(encoding='utf-8')
    t = re.sub(r'<!--\s*\n=+.*?-->\n', '', t, count=1, flags=re.S)  # drop the authoring guide comment
    for marker in ('BUILD:SIDEBAR', 'BUILD:MAIN'):
        if f'<!-- {marker} -->' not in t or f'<!-- /{marker} -->' not in t:
            sys.exit(f'Template is missing the <!-- {marker} --> markers.')
    return t


def fill(template, *, sidebar, main, layout, values, home_href):
    out = re.sub(r'<!-- BUILD:SIDEBAR -->.*?<!-- /BUILD:SIDEBAR -->', lambda m: sidebar, template, count=1, flags=re.S)
    out = re.sub(r'<!-- BUILD:MAIN -->.*?<!-- /BUILD:MAIN -->', lambda m: main.strip() + '\n', out, count=1, flags=re.S)
    out = re.sub(r'<!-- The "On this page" TOC is inserted here by the script. -->\n', '', out)
    out = re.sub(r'<body data-layout="[^"]*">', f'<body data-layout="{layout}">', out, count=1)
    out = out.replace('<a class="header-title" href="index.html">', f'<a class="header-title" href="{esc(home_href)}">', 1)
    for key, val in values.items():
        out = out.replace('{{' + key + '}}', esc(val))
    return out


def check_fragment(frag, name):
    for tag in ('<html', '<head', '<body', '<style', '<script'):
        if tag in frag.lower():
            sys.exit(f'{name}: fragment must not contain {tag}...>. Give only the inner content of <main>.')


# ── Images ───────────────────────────────────────────────────────────────────

def is_local(src):
    return not re.match(r'^(data:|https?:|//|#)', src, re.I)


def embed_images(frag, base_dir):
    def repl(m):
        src = html.unescape(m.group(2))
        if not is_local(src):
            return m.group(0)
        path = (base_dir / src).resolve()
        if not path.is_file():
            warnings.append(f'image not found, left as is: {src}')
            return m.group(0)
        mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        if path.suffix.lower() == '.svg':
            mime = 'image/svg+xml'
        data = base64.b64encode(path.read_bytes()).decode('ascii')
        return f'{m.group(1)}data:{mime};base64,{data}{m.group(3)}'
    return IMG_SRC.sub(repl, frag)


def copy_images(frag, base_dir, out_dir, copied):
    img_dir = out_dir / 'images'

    def repl(m):
        src = html.unescape(m.group(2))
        if not is_local(src):
            return m.group(0)
        path = (base_dir / src).resolve()
        if not path.is_file():
            warnings.append(f'image not found, left as is: {src}')
            return m.group(0)
        if path not in copied:
            img_dir.mkdir(parents=True, exist_ok=True)
            name = re.sub(r'[^\w.-]+', '-', path.name)
            dest = img_dir / name
            if dest.exists() and dest.read_bytes() != path.read_bytes():
                digest = hashlib.sha1(path.read_bytes()).hexdigest()[:8]
                dest = img_dir / f'{dest.stem}-{digest}{dest.suffix}'
            shutil.copyfile(path, dest)
            copied[path] = f'images/{dest.name}'
        return f'{m.group(1)}{esc(copied[path])}{m.group(3)}'
    return IMG_SRC.sub(repl, frag)


# ── Single-file mode ─────────────────────────────────────────────────────────

def build_single(args):
    content_path = Path(args.content)
    frag = content_path.read_text(encoding='utf-8')
    check_fragment(frag, content_path.name)

    used = set(re.findall(r'\bid="([^"]+)"', frag))
    chapters = []

    def add_id(m):
        level, attrs, inner = m.group(1), m.group(2) or '', m.group(3)
        label = text_of(inner)
        idm = re.search(r'\bid="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(label, used)
        if not idm:
            attrs = f' id="{hid}"' + attrs
        if level == '2':
            icon = re.search(r'\bdata-icon="([^"]+)"', attrs)
            chapters.append({'label': label, 'href': f'#{hid}', 'icon': icon.group(1) if icon else 'file', 'children': []})
        elif chapters:
            chapters[-1]['children'].append((label, f'#{hid}'))
        return f'<h{level}{attrs}>{inner}</h{level}>'

    frag = HEADING.sub(add_id, frag)
    if not chapters:
        warnings.append('no <h2> headings found, so the sidebar is empty')
    if not args.no_embed:
        frag = embed_images(frag, content_path.parent)

    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', frag, re.S)
    title = args.title or (text_of(h1.group(1)) if h1 else args.product)
    values = {
        'PRODUCT_NAME': args.product,
        'PAGE_TITLE': title,
        'HEADER_TITLE': args.header_title or f'{args.product} Documentation',
        'YEAR': args.year,
    }
    page = fill(load_template(), sidebar=sidebar_html(('Home', '#'), chapters, open_first=True),
                main=frag, layout='document', values=values, home_href='#')
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding='utf-8')
    print(f'Wrote {out} ({out.stat().st_size / 1024:.0f} KB, {len(chapters)} chapters)')


# ── Site mode ────────────────────────────────────────────────────────────────

def hub_fragment(section, eyebrow):
    tiles = []
    for p in section.get('pages', []):
        tiles.append(
            f'  <a class="hub-tile" href="{esc(p["file"])}">\n'
            f'    <div class="hub-icon">{svg(p.get("icon") or section.get("icon") or "file", 20, 1.8)}</div>\n'
            f'    <div class="hub-title">{esc(p["label"])}</div>\n'
            f'    <div class="hub-desc">{esc(p.get("desc", ""))}</div>\n'
            f'    <div class="hub-arrow">View guide {svg_raw(ARROW, 12, 2.5)}</div>\n'
            f'  </a>')
        if not p.get('desc'):
            warnings.append(f'{section["file"]}: hub tile "{p["label"]}" has no "desc" in NAV.json')
    return (f'<div class="cover">\n  <div class="eyebrow">{esc(eyebrow)}</div>\n  <h1>{esc(section["label"])}</h1>\n'
            f'  <p class="subtitle">{esc(section.get("desc", ""))}</p>\n</div>\n\n'
            f'<div class="hub-grid">\n' + '\n'.join(tiles) + '\n</div>\n')


def build_site(args):
    nav = json.loads(Path(args.nav).read_text(encoding='utf-8'))
    src, out = Path(args.src), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    product = nav['product']
    home = nav.get('home', {})
    home_file = home.get('file', 'index.html')
    values_base = {
        'PRODUCT_NAME': product,
        'HEADER_TITLE': nav.get('headerTitle', f'{product} Documentation'),
        'YEAR': str(nav.get('year', datetime.date.today().year)),
    }
    eyebrow = nav.get('eyebrow', 'Documentation')

    # Reading order: home, then each hub followed by its pages.
    order = [{'file': home_file, 'label': home.get('title', 'Home'), 'kind': 'home', 'appRoute': home.get('appRoute')}]
    for s in nav['sections']:
        order.append({**s, 'kind': 'hub'})
        for p in s.get('pages', []):
            order.append({**p, 'kind': 'page', 'section': s})

    side_sections = [{'label': s['label'], 'href': s['file'], 'icon': s.get('icon'),
                      'children': [(p['label'], p['file']) for p in s.get('pages', [])]} for s in nav['sections']]
    template = load_template()
    copied, errors, help_map = {}, [], []

    for i, item in enumerate(order):
        path = src / item['file']
        if path.exists():
            frag = path.read_text(encoding='utf-8')
            check_fragment(frag, item['file'])
        elif item['kind'] == 'hub':
            frag = hub_fragment(item, eyebrow)
        else:
            errors.append(f'missing content fragment: {path}')
            continue

        layout = {'home': 'landing', 'hub': 'hub', 'page': 'article'}[item['kind']]
        if layout == 'landing' and 'class="landing"' not in frag:
            frag = f'<div class="landing">\n{frag}\n</div>'
        if layout == 'article' and 'class="breadcrumb"' not in frag:
            s = item['section']
            frag = (f'<nav class="breadcrumb" aria-label="Breadcrumb">\n  <a href="{esc(s["file"])}">{esc(s["label"])}</a>\n'
                    f'  <span class="bc-sep">›</span>\n  <span class="bc-current">{esc(item["label"])}</span>\n</nav>\n\n') + frag
        if layout != 'landing' and 'class="page-nav"' not in frag:
            btns = []
            if i > 0:
                btns.append(f'<a class="btn secondary" href="{esc(order[i - 1]["file"])}">Previous</a>')
            if i < len(order) - 1:
                btns.append(f'<a class="btn" href="{esc(order[i + 1]["file"])}">Next</a>')
            frag += '\n\n<footer class="page-nav">\n  ' + '\n  '.join(btns) + '\n</footer>\n'
        frag = copy_images(frag, path.parent if path.exists() else src, out, copied)

        values = {**values_base, 'PAGE_TITLE': item['label']}
        page = fill(template, sidebar=sidebar_html(('Home', home_file), side_sections, current=item['file']),
                    main=frag, layout=layout, values=values, home_href=home_file)
        (out / item['file']).write_text(page, encoding='utf-8')

        if item.get('appRoute'):
            help_map.append({'appRoute': item['appRoute'], 'appPageName': item.get('appPageName', item['label']),
                             'docPage': item['file'], 'docPageId': Path(item['file']).stem, 'docTitle': item['label']})

    if help_map:
        (out / 'help-map.json').write_text(json.dumps({
            '_readme': 'Maps each product app route to its help page. The app opens docPage when the user selects Help on appRoute.',
            'pages': help_map}, indent=2), encoding='utf-8')
    print(f'Wrote {len(order) - len(errors)} pages to {out}' + (f', help-map.json ({len(help_map)} routes)' if help_map else ''))
    if errors:
        print('ERRORS:\n  ' + '\n  '.join(errors))
        return 1
    return 0


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='mode', required=True)
    s = sub.add_parser('single', help='one self-contained HTML file')
    s.add_argument('content')
    s.add_argument('--out', required=True)
    s.add_argument('--product', required=True)
    s.add_argument('--title')
    s.add_argument('--header-title')
    s.add_argument('--year', default=str(datetime.date.today().year))
    s.add_argument('--no-embed', action='store_true', help='keep image paths instead of embedding base64')
    w = sub.add_parser('site', help='multi-page web help')
    w.add_argument('nav')
    w.add_argument('--src', required=True)
    w.add_argument('--out', required=True)
    args = ap.parse_args()

    code = build_single(args) if args.mode == 'single' else build_site(args)
    for w_ in dict.fromkeys(warnings):
        print(f'WARNING: {w_}')
    sys.exit(code or 0)


if __name__ == '__main__':
    main()
