#!/usr/bin/env python3
"""소재 HTML 시안의 '제품 컷' 자리(회색 박스)를 누끼 제품 이미지로 바꾼다.

사용법: python3 team/tools/place_product.py <banner 폴더> <누끼 png 경로(banner 폴더 기준 상대경로로 기록)> [--dry-run]
- 대상: <div class="box" style="...">…제품 컷…</div>
- 박스 위치·크기는 그대로 두고 배경·테두리·라벨만 지운 뒤, 제품을 박스 안에 비율 유지로 넣는다(그림자 포함).
- 원본은 같은 폴더의 .orig/ 에 한 번만 백업한다. 다시 실행하면 백업본 기준으로 다시 만든다.
"""
import argparse
import os
import pathlib
import re
import shutil

BOX = re.compile(r'<div class="box" style="([^"]*)">((?:(?!</div>).)*?제품 컷(?:(?!</div>).)*?)</div>', re.S)


def replace(html, img_rel):
    def sub(m):
        style = re.sub(r"(background|border)[^;]*;?", "", m.group(1)).rstrip(";")
        return (f'<div class="box" style="{style};background:transparent;border:0">'
                f'<img src="{img_rel}" alt="제품" style="width:100%;height:100%;object-fit:contain;'
                f'filter:drop-shadow(0 18px 24px rgba(0,0,0,.18))"></div>')
    return BOX.subn(sub, html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("banner_dir")
    ap.add_argument("cutout")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    d = pathlib.Path(a.banner_dir)
    backup = d / ".orig"
    backup.mkdir(exist_ok=True)
    rel = os.path.relpath(pathlib.Path(a.cutout).resolve(), d.resolve())
    total = 0
    for f in sorted(d.glob("*.html")):
        src = backup / f.name
        if not src.exists():
            shutil.copy2(f, src)
        html, n = replace(src.read_text(encoding="utf-8"), rel)
        if n and not a.dry_run:
            f.write_text(html, encoding="utf-8")
        total += n
        print(f"{f.stem}\t{n}개 교체" if n else f"{f.stem}\t제품 자리 없음")
    print(f"총 {total}개 박스 교체 (이미지: {rel})")


if __name__ == "__main__":
    main()
