"""Check built HTML docs against the template before delivery.

Usage:
    python check_html.py PATH [PATH ...]     (an .html file or a folder of them)

ERRORS (must fix):
  - CSS or JS differs from the template (styling was edited or added)
  - inline style="" attributes, extra <style> or <script> blocks
  - CSS classes the template doesn't define
  - leftover {{PLACEHOLDERS}}, duplicate ids, broken #anchors,
    broken links to local .html files, missing image files, <img> without alt
WARNINGS (review):
  - not exactly one <h1>, skipped heading levels, <section> without <h2>
  - step numbers not 1, 2, 3... in a .steps block, empty alt text
  - TODO / TBD / XX markers, files over 15 MB

Exit code 1 if any errors. Standard library only.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / 'assets' / 'html-doc-template.html'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
STYLE_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.S | re.I)
SCRIPT_RE = re.compile(r'<script[^>]*>(.*?)</script>', re.S | re.I)
COMMENT_RE = re.compile(r'<!--.*?-->', re.S)


def template_parts():
    t = COMMENT_RE.sub('', TEMPLATE.read_text(encoding='utf-8'))
    css = STYLE_RE.findall(t)[0]
    js = SCRIPT_RE.findall(t)          # all script blocks, in order (theme init in <head>, behaviour at the end)
    classes = set(re.findall(r'\.(-?[_a-zA-Z][\w-]*)', css))
    return css, js, classes


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, attrs)
        self.classes = {}        # class -> first line
        self.ids = {}
        self.dup_ids = []
        self.hrefs = []          # (href, line)
        self.imgs = []           # (src, alt or None, line)
        self.headings = []       # (level, line)
        self.inline_styles = []
        self.sections = []       # [line, has_h2]
        self.steps = []          # list of lists of step-num texts
        self.in_step_num = False
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        for c in (a.get('class') or '').split():
            self.classes.setdefault(c, line)
        if 'id' in a:
            if a['id'] in self.ids:
                self.dup_ids.append((a['id'], line))
            self.ids[a['id']] = line
        if 'style' in a:
            self.inline_styles.append((tag, line))
        if tag == 'a' and a.get('href'):
            self.hrefs.append((a['href'], line))
        if tag == 'img':
            self.imgs.append((a.get('src', ''), a.get('alt'), line))
        if re.fullmatch(r'h[1-6]', tag):
            self.headings.append((int(tag[1]), line))
            if tag == 'h2':
                for t, at in reversed(self.stack):
                    if t == 'section':
                        at['_has_h2'] = True
                        break
        if tag == 'section':
            a['_line'] = line
            a['_has_h2'] = 'lp-hero' in (a.get('class') or '')  # the landing hero needs no h2
        cls = (a.get('class') or '').split()
        if 'steps' in cls:
            self.steps.append([])
        if 'step-num' in cls:
            self.in_step_num = True
        if tag not in VOID:
            self.stack.append((tag, a))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                t, a = self.stack[i]
                if t == 'section':
                    self.sections.append((a['_line'], a['_has_h2']))
                del self.stack[i:]
                break
        if tag == 'div':
            self.in_step_num = False

    def handle_data(self, data):
        if self.in_step_num and self.steps and data.strip():
            self.steps[-1].append(data.strip())
        if not any(t in ('script', 'style') for t, _ in self.stack):
            self.text.append((data, self.getpos()[0]))


def check(path, tpl_css, tpl_js, tpl_classes):
    errors, warns = [], []
    src = path.read_text(encoding='utf-8')

    bare = COMMENT_RE.sub('', src)
    styles, scripts = STYLE_RE.findall(bare), SCRIPT_RE.findall(bare)
    if len(styles) != 1:
        errors.append(f'expected exactly 1 <style> block (the template\'s), found {len(styles)}')
    elif styles[0] != tpl_css:
        errors.append('CSS differs from the template: do not edit or add styles; rebuild with build_html.py')
    if len(scripts) != len(tpl_js):
        errors.append(f'expected exactly {len(tpl_js)} <script> blocks (the template\'s), found {len(scripts)}')
    elif scripts != tpl_js:
        errors.append('JavaScript differs from the template: rebuild with build_html.py')

    p = Scan()
    p.feed(src)

    for tag, line in p.inline_styles:
        errors.append(f'line {line}: inline style="" on <{tag}>; use template classes instead')
    for c, line in sorted(p.classes.items(), key=lambda x: x[1]):
        if c not in tpl_classes:
            errors.append(f'line {line}: class "{c}" is not defined by the template')
    for m in re.finditer(r'\{\{[A-Z_]+\}\}', src):
        errors.append(f'line {src.count(chr(10), 0, m.start()) + 1}: leftover placeholder {m.group(0)}')
    for i, line in p.dup_ids:
        errors.append(f'line {line}: duplicate id "{i}"')

    for href, line in p.hrefs:
        if href.startswith('#'):
            if len(href) > 1 and href[1:] not in p.ids:
                errors.append(f'line {line}: link to missing anchor {href}')
        elif not re.match(r'^[a-z][a-z0-9+.-]*:|^//', href, re.I):
            target = href.split('#')[0].split('?')[0]
            if target and not (path.parent / target).exists():
                errors.append(f'line {line}: link to missing file {target}')

    for s, alt, line in p.imgs:
        if alt is None:
            errors.append(f'line {line}: <img> without alt text')
        elif not alt.strip():
            warns.append(f'line {line}: <img> has empty alt text; describe the screenshot')
        if s and not re.match(r'^(data:|https?:|//)', s, re.I) and not (path.parent / s).exists():
            errors.append(f'line {line}: image file not found: {s}')

    h1 = [l for lv, l in p.headings if lv == 1]
    if len(h1) != 1:
        warns.append(f'expected 1 <h1>, found {len(h1)}' + (f' (lines {", ".join(map(str, h1))})' if h1 else ''))
    prev = 1
    for lv, line in p.headings:
        if lv > prev + 1:
            warns.append(f'line {line}: heading jumps from h{prev} to h{lv}')
        prev = lv
    for line, has_h2 in p.sections:
        if not has_h2:
            warns.append(f'line {line}: <section> has no <h2>')
    for nums in p.steps:
        if nums != [str(i) for i in range(1, len(nums) + 1)]:
            warns.append(f'steps numbered {", ".join(nums)}; expected 1 to {len(nums)}')

    for data, line in p.text:
        for m in re.finditer(r'\bTODO\b|\bTBD\b|\bTBC\b|\bXX+\b|lorem ipsum', data, re.I):
            warns.append(f'line {line}: placeholder text "{m.group(0)}"')

    size = path.stat().st_size / 1024 / 1024
    if size > 15:
        warns.append(f'file is {size:.1f} MB; consider compressing screenshots')
    return errors, warns


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    files = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        files.extend(sorted(p.glob('*.html')) if p.is_dir() else [p])
    tpl_css, tpl_js, tpl_classes = template_parts()
    total_err = 0
    for f in files:
        errors, warns = check(f, tpl_css, tpl_js, tpl_classes)
        total_err += len(errors)
        status = 'FAIL' if errors else 'OK'
        print(f'{status}  {f}  ({len(errors)} errors, {len(warns)} warnings)')
        for e in errors:
            print(f'  ERROR    {e}')
        for w in warns:
            print(f'  WARNING  {w}')
    sys.exit(1 if total_err else 0)


if __name__ == '__main__':
    main()
