"""Builds team-F-p3.pdf from INFORME.md with headless Chrome.

Needs tools/requirements-report.txt and Google Chrome (or the browser named by CHROME).
"""
import os
import pathlib
import re
import subprocess
import tempfile

from markdown_it import MarkdownIt

HERE = pathlib.Path(__file__).resolve().parent.parent
CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

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
"""


def to_html(text):
    html = MarkdownIt('commonmark').enable('table').render(text)
    # The views are much wider than they are tall: each one gets its own landscape page.
    return re.sub(r'(<p><img [^>]*view-(?:operation|coordination)[^>]*></p>\s*<p>.*?</p>)',
                  r'<div class="wide">\1</div>', html, flags=re.S)


if __name__ == '__main__':
    body = to_html((HERE / 'INFORME.md').read_text(encoding='utf-8'))
    page = (f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
            f'<base href="{HERE.as_uri()}/"><title>Entrega 3, equipo F</title>'
            f'<style>{STYLE}</style></head><body>{body}</body></html>')
    target = HERE / 'team-F-p3.pdf'
    with tempfile.TemporaryDirectory() as tmp:
        source = pathlib.Path(tmp) / 'report.html'
        source.write_text(page, encoding='utf-8')
        subprocess.run([CHROME, '--headless=new', '--no-pdf-header-footer',
                        '--allow-file-access-from-files', f'--user-data-dir={tmp}/profile',
                        f'--print-to-pdf={target}', source.as_uri()], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f'{target.name} written')
