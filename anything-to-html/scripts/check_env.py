"""Report which document converters are available on this machine, and what
each input format can be converted with. Never installs anything.

Usage:
    python check_env.py            readable report
    python check_env.py --json     machine-readable report (for agents)

Run it only after the user has agreed to a scan of installed software.
Standard library only. Takes a few seconds (it runs `pandoc --version`,
tries a few imports, and on Windows checks the built-in OCR engine).
"""
import importlib
import json
import platform
import shutil
import subprocess
import sys

IS_WIN = platform.system() == 'Windows'
IS_MAC = platform.system() == 'Darwin'


def run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or '') + (r.stderr or '')
    except (OSError, subprocess.TimeoutExpired):
        return 1, ''


def module(name):
    try:
        m = importlib.import_module(name)
        return getattr(m, '__version__', None) or getattr(m, 'version', None) or 'yes'
    except Exception:
        return None


def pandoc_info():
    exe = shutil.which('pandoc')
    if not exe:
        return None
    _, out = run([exe, '--version'])
    version = out.split('\n', 1)[0].replace('pandoc', '').strip() if out else '?'
    _, formats = run([exe, '--list-input-formats'])
    return {'path': exe, 'version': version, 'inputs': set(formats.split())}


def windows_ocr():
    """True if the built-in Windows OCR engine (Windows.Media.Ocr) has a language installed."""
    if not IS_WIN or not shutil.which('powershell'):
        return None
    ps = ('[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime] > $null; '
          '$l=[Windows.Media.Ocr.OcrEngine]::AvailableRecognizerLanguages; '
          'Write-Output (($l | ForEach-Object { $_.LanguageTag }) -join ",")')
    code, out = run(['powershell', '-NoProfile', '-NonInteractive', '-Command', ps], timeout=30)
    langs = out.strip().split('\n')[-1].strip() if code == 0 and out.strip() else ''
    return langs or None


def browser():
    cands = ['msedge', 'chrome', 'google-chrome', 'chromium', 'chromium-browser']
    paths = [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
             r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
             r'C:\Program Files\Google\Chrome\Application\chrome.exe',
             '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
             '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']
    for c in cands:
        if shutil.which(c):
            return shutil.which(c)
    import os
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def pick(options):
    """Return the first (label, available) whose available is truthy."""
    for label, ok in options:
        if ok:
            return label
    return None


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    as_json = '--json' in sys.argv

    pandoc = pandoc_info()
    pin = pandoc['inputs'] if pandoc else set()
    mods = {m: module(m) for m in ('pymupdf', 'pypdf', 'pdfplumber', 'pymupdf4llm', 'pptx', 'openpyxl', 'docx',
                                   'markitdown', 'docling', 'pytesseract', 'pdf2image')}
    cli = {c: shutil.which(c) for c in ('pdftotext', 'pdfimages', 'pdftoppm', 'tesseract', 'soffice', 'libreoffice',
                                        'markitdown', 'mineru', 'magic-pdf', 'swift')}
    import os
    if IS_MAC and not cli['soffice'] and os.path.exists('/Applications/LibreOffice.app/Contents/MacOS/soffice'):
        cli['soffice'] = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    win_ocr = windows_ocr()
    mac_ocr = IS_MAC and cli['swift']   # Apple Vision through scripts/ocr_macos.swift (Xcode Command Line Tools)
    chrome = browser()
    py_ok = sys.version_info >= (3, 8)

    pip = f'{sys.executable} -m pip install'
    installs = {
        'pandoc': 'winget install JohnMacFarlane.Pandoc' if IS_WIN else ('brew install pandoc' if IS_MAC else 'sudo apt install pandoc') + '   (or https://pandoc.org/installing.html)',
        'pymupdf': f'{pip} pymupdf   (AGPL-3.0 licence; fine to run locally)',
        'markitdown': f'{pip} "markitdown[pdf,docx,pptx,xlsx]"   (MIT; pure Python fallback for every format)',
        'tesseract': 'winget install UB-Mannheim.TesseractOCR' if IS_WIN else ('brew install tesseract' if IS_MAC else 'sudo apt install tesseract-ocr'),
        'poppler': 'winget install oschwartz10612.Poppler' if IS_WIN else ('brew install poppler' if IS_MAC else 'sudo apt install poppler-utils'),
        'python-pptx': f'{pip} python-pptx',
        'openpyxl': f'{pip} openpyxl',
        'docling': f'{pip} docling   (large: PyTorch + models on first run; best tables and OCR)',
        'xcode-clt': 'xcode-select --install   (macOS: provides the swift command used by the built-in Vision OCR)',
    }

    # What each input can be converted with, first choice first.
    caps = {
        'docx': pick([('pandoc', 'docx' in pin), ('markitdown', mods['markitdown'] or cli['markitdown']), ('python-docx', mods['docx'])]),
        'pptx': pick([('pandoc', 'pptx' in pin), ('markitdown', mods['markitdown'] or cli['markitdown']), ('python-pptx', mods['pptx'])]),
        'xlsx': pick([('pandoc', 'xlsx' in pin), ('markitdown', mods['markitdown'] or cli['markitdown']), ('openpyxl', mods['openpyxl'])]),
        'csv/tsv': pick([('pandoc', 'csv' in pin), ('python csv module', True)]),
        'odt/rtf/epub': pick([('pandoc', {'odt', 'rtf', 'epub'} <= pin), ('markitdown (epub only)', mods['markitdown'])]),
        'html/markdown': 'pandoc' if pandoc else 'read directly',
        'pdf (text layer)': pick([('pymupdf via extract_pdf.py', mods['pymupdf']), ('pdfplumber', mods['pdfplumber']),
                                  ('markitdown', mods['markitdown']), ('pdftotext', cli['pdftotext']), ('pypdf (text only)', mods['pypdf'])]),
        'pdf images': pick([('pymupdf', mods['pymupdf']), ('pdfimages', cli['pdfimages'])]),
        'pdf (scanned, needs OCR)': pick([('tesseract + pymupdf', cli['tesseract'] and mods['pymupdf']),
                                          ('Windows built-in OCR + pymupdf', win_ocr and mods['pymupdf']),
                                          ('macOS Vision OCR (swift) + pymupdf', mac_ocr and mods['pymupdf']),
                                          ('docling', mods['docling']),
                                          ('pytesseract + pdf2image', mods['pytesseract'] and mods['pdf2image'] and cli['pdftoppm'])]),
        'screenshot of the result': 'headless Edge/Chrome' if chrome else None,
    }
    options = {
        'docx': ['pandoc', 'markitdown'], 'pptx': ['pandoc', 'markitdown', 'python-pptx'], 'xlsx': ['pandoc', 'markitdown', 'openpyxl'],
        'odt/rtf/epub': ['pandoc'], 'pdf (text layer)': ['pymupdf', 'markitdown'], 'pdf images': ['pymupdf', 'poppler'],
        'pdf (scanned, needs OCR)': ['tesseract'] + (['xcode-clt'] if IS_MAC else []) + ['docling'], 'screenshot of the result': [],
    }

    report = {
        'python': {'version': platform.python_version(), 'ok': py_ok, 'executable': sys.executable},
        'pandoc': {'version': pandoc['version'], 'path': pandoc['path']} if pandoc else None,
        'python_modules': mods,
        'cli_tools': cli,
        'windows_ocr_languages': win_ocr,
        'macos_vision_ocr': bool(mac_ocr),
        'platform': platform.system(),
        'browser': chrome,
        'capabilities': caps,
        'install_options': {k: {name: installs[name] for name in v if name in installs} for k, v in options.items() if not caps.get(k)},
    }
    if as_json:
        print(json.dumps(report, indent=2, default=str))
        return

    print(f'Python {platform.python_version()} ({sys.executable}){"" if py_ok else "  -- 3.8+ needed"}')
    print(f'Pandoc {pandoc["version"]} ({pandoc["path"]})' if pandoc else 'Pandoc: not found')
    found = [f'{k} {v}' if v not in (None, 'yes') else k for k, v in mods.items() if v]
    print('Python modules: ' + (', '.join(found) if found else 'none of the optional ones'))
    found = [k for k, v in cli.items() if v]
    print('Command-line tools: ' + (', '.join(found) if found else 'none of the optional ones'))
    if IS_WIN:
        print(f'Windows built-in OCR: {"languages " + win_ocr if win_ocr else "not available"}')
    if IS_MAC:
        print(f'macOS Vision OCR (needs swift from Xcode Command Line Tools): {"available" if mac_ocr else "not available"}')
    print(f'Browser for screenshots: {chrome or "not found"}')
    print()
    print('What works now (no installation):')
    for k, v in caps.items():
        print(f'  {k:28} {v or "-- not possible yet"}')
    missing = report['install_options']
    if missing:
        print()
        print('Options for what is missing (ask the user before installing anything):')
        for k, opts in missing.items():
            print(f'  {k}:')
            for name, cmd in opts.items():
                print(f'      {name:12} {cmd}')
    print()
    print('Nothing was installed or changed.')


if __name__ == '__main__':
    main()
