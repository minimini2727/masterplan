#!/usr/bin/env python3
"""마크다운 문서를 페이퍼로지(Paperlogy) 폰트 PDF로 변환한다.

사용법: python3 team/tools/md_to_pdf.py <입력.md> <출력.pdf> [문서 제목]
필요: pip markdown, node + playwright(사전 설치된 Chromium)
"""
import pathlib
import subprocess
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parents[2]
FONT_DIR = ROOT / "team" / "assets" / "fonts"

CSS = """
@page { size: A4; margin: 18mm 15mm 18mm 15mm; }
%FONTS%
:root { --ink:#1d1d1f; --muted:#6b6b70; --accent:#2f5d50; --line:#d9d9de; --soft:#f4f6f5; }
* { box-sizing: border-box; }
body { font-family: 'Paperlogy', sans-serif; font-weight: 400; color: var(--ink);
       font-size: 9.6pt; line-height: 1.6; margin: 0; word-break: keep-all; }
.cover { border-bottom: 3px solid var(--accent); padding-bottom: 10mm; margin-bottom: 8mm; }
.cover .eyebrow { color: var(--accent); font-weight: 600; letter-spacing: .08em; font-size: 9pt; }
.cover h1 { font-size: 24pt; font-weight: 700; margin: 4mm 0 2mm; border: 0; padding: 0; }
.cover .meta { color: var(--muted); font-size: 9pt; }
h1 { font-size: 17pt; font-weight: 700; margin: 8mm 0 3mm; }
h2 { font-size: 13.5pt; font-weight: 700; color: var(--accent); margin: 8mm 0 3mm;
     padding-bottom: 1.5mm; border-bottom: 1px solid var(--line); break-after: avoid; }
h3 { font-size: 11pt; font-weight: 600; margin: 5mm 0 2mm; break-after: avoid; }
h4 { font-size: 10pt; font-weight: 600; margin: 4mm 0 1.5mm; }
p, li { margin: 1.2mm 0; }
ul, ol { padding-left: 5mm; }
strong { font-weight: 700; }
code { font-family: 'Paperlogy', monospace; background: var(--soft); padding: 0 1mm; border-radius: 2px; font-size: 8.8pt; }
pre { background: var(--soft); padding: 3mm; border-radius: 3px; white-space: pre-wrap; font-size: 8.5pt; }
blockquote { margin: 3mm 0; padding: 2mm 4mm; border-left: 3px solid var(--accent); background: var(--soft); color: #333; }
table { width: 100%; border-collapse: collapse; margin: 3mm 0 4mm; font-size: 8.2pt; line-height: 1.45; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: var(--accent); color: #fff; font-weight: 600; text-align: left; padding: 1.6mm 2mm; }
td { border-bottom: 1px solid var(--line); padding: 1.4mm 2mm; vertical-align: top; }
tbody tr:nth-child(even) td { background: #fafafa; }
hr { border: 0; border-top: 1px solid var(--line); margin: 6mm 0; }
a { color: var(--accent); text-decoration: none; word-break: break-all; }
"""


def font_faces() -> str:
    faces = []
    for f in sorted(FONT_DIR.glob("Paperlogy-*.woff2")):
        weight = f.stem.split("-")[1]
        faces.append(
            "@font-face { font-family:'Paperlogy'; font-weight:%s; font-style:normal;"
            " src:url('%s') format('woff2'); }" % (weight, f.as_uri())
        )
    if not faces:
        sys.exit(f"폰트가 없습니다: {FONT_DIR}")
    return "\n".join(faces)


def fix_lists(md_text: str) -> str:
    """목록·표 앞에 빈 줄이 없으면 python-markdown이 문단으로 합치므로 빈 줄을 넣는다."""
    import re
    out, prev = [], ""
    for line in md_text.splitlines():
        starts_block = re.match(r"^\s*([-*+]|\d+\.)\s+", line) or line.lstrip().startswith("|")
        prev_block = re.match(r"^\s*([-*+]|\d+\.)\s+", prev) or prev.lstrip().startswith("|")
        if starts_block and prev.strip() and not prev_block:
            out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)


def build_html(md_text: str, title: str, meta: str) -> str:
    body = markdown.markdown(fix_lists(md_text), extensions=["tables", "fenced_code", "sane_lists"])
    css = CSS.replace("%FONTS%", font_faces())
    cover = (
        f'<div class="cover"><div class="eyebrow">PERFORMANCE MARKETING</div>'
        f"<h1>{title}</h1><div class=\"meta\">{meta}</div></div>"
    )
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{css}</style></head><body>{cover}{body}</body></html>'


NODE = r"""
const { chromium } = require('playwright');
(async () => {
  const [html, pdf, footer] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + html, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: pdf, format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: `<div style="width:100%;font-family:sans-serif;font-size:7pt;color:#888;padding:0 15mm;display:flex;justify-content:space-between;"><span>${footer}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>` });
  await b.close();
})();
"""


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src = pathlib.Path(sys.argv[1]).resolve()
    out = pathlib.Path(sys.argv[2]).resolve()
    title = sys.argv[3] if len(sys.argv) > 3 else src.stem
    md_text = src.read_text(encoding="utf-8")
    meta = f"원본: {src.relative_to(ROOT) if src.is_relative_to(ROOT) else src.name}"
    html_path = out.with_suffix(".html")
    html_path.write_text(build_html(md_text, title, meta), encoding="utf-8")
    js = out.with_suffix(".render.js")
    js.write_text(NODE, encoding="utf-8")
    try:
        subprocess.run(["node", str(js), str(html_path), str(out), title], check=True)
    finally:
        js.unlink(missing_ok=True)
        html_path.unlink(missing_ok=True)
    print(out)


if __name__ == "__main__":
    main()
