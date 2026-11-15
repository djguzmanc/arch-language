"""Builds team-F-p4.pdf from INFORME-P4.md with headless Chrome (copy of build_report.py).

Usage: python tools/build_report_p4.py [output.pdf]   (default: team-F-p4.pdf in the repo)

Needs tools/requirements-report.txt and Google Chrome (or the browser named by CHROME).
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from markdown_it import MarkdownIt

HERE = pathlib.Path(__file__).resolve().parent.parent
CHROME = os.environ.get('CHROME') or next(
    (c for c in ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                 shutil.which('google-chrome'), shutil.which('chromium'),
                 shutil.which('chromium-browser')) if c and os.path.exists(c)), 'google-chrome')

STYLE = """
@page { size: A4; margin: 18mm 16mm; }
@page wide { size: A4 landscape; margin: 12mm; }
body { font: 10.5pt/1.42 Helvetica, Arial, sans-serif; color: #1a1a1a; }
h1 { font-size: 19pt; margin: 0 0 6pt; }
h2 { font-size: 14pt; margin: 20pt 0 6pt; border-bottom: 1px solid #999; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin: 14pt 0 5pt; }
h4 { font-size: 10.5pt; margin: 12pt 0 4pt; }
h2, h3, h4 { break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 7pt 0 10pt; font-size: 9pt; break-inside: avoid; }
th, td { border: 1px solid #aaa; padding: 3pt 5pt; text-align: left; vertical-align: top; overflow-wrap: break-word; }
th { background: #eee; }
tr { break-inside: avoid; }
code { font: 8.8pt Menlo, Consolas, monospace; background: #f2f2f2; padding: 0 2pt; }
pre { background: #f6f6f6; border: 1px solid #ddd; padding: 6pt; white-space: pre-wrap; overflow-wrap: anywhere; }
pre code { font-size: 7.8pt; background: none; padding: 0; }
img { display: block; max-width: 100%; margin: 0 auto; }
.wide { page: wide; }
.wide img { max-height: 170mm; width: 100%; object-fit: contain; }
mark { background: #fff1a8; }
blockquote { border-left: 3px solid #ccc; margin: 6pt 0; padding: 2pt 8pt; color: #444; }
"""


def to_html(text):
    html = MarkdownIt('commonmark').enable('table').render(text)
    # Draft markers [[PENDIENTE: ...]], [[CIFRA: ...]], [[CONFIRMAR: ...]] are highlighted.
    html = re.sub(r'\[\[.*?\]\]+', lambda m: f'<mark>{m.group(0)}</mark>', html)
    # The views and the graphs are wider than they are tall: each one gets its own landscape page.
    return re.sub(r'(<p><img [^>]*(?:view-(?:operation|coordination)|graph\.png)[^>]*></p>\s*<p>.*?</p>)',
                  r'<div class="wide">\1</div>', html, flags=re.S)


if __name__ == '__main__':
    body = to_html((HERE / 'INFORME-P4.md').read_text(encoding='utf-8'))
    page = (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f'<base href="{HERE.as_uri()}/"><title>Entrega 4, equipo F</title>'
            f'<style>{STYLE}</style></head><body>{body}</body></html>')
    target = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / 'team-F-p4.pdf'
    with tempfile.TemporaryDirectory() as tmp:
        source = pathlib.Path(tmp) / 'report.html'
        source.write_text(page, encoding='utf-8')
        subprocess.run([CHROME, '--headless=new', '--no-pdf-header-footer',
                        '--allow-file-access-from-files', f'--user-data-dir={tmp}/profile',
                        '--no-sandbox', f'--print-to-pdf={target}', source.as_uri()], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f'{target.name} written')
