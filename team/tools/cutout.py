#!/usr/bin/env python3
"""제품 사진의 배경을 지워(누끼) 투명 PNG로 만든다.

사용법: python3 -I team/tools/cutout.py <입력 이미지> <출력.png> [--model u2net|isnet-general-use]
- rembg(로컬 AI 배경 제거)를 쓴다. 첫 실행 때 모델(약 170MB)을 GitHub에서 받는다.
- 결과는 제품 영역에 맞춰 여백을 잘라내고(투명 영역 trim) 사방 2% 여유를 둔다.
- 입력 이미지는 외부에서 받은 파일이므로 이 스크립트는 이미지 픽셀만 읽는다.
"""
import argparse
import pathlib

from PIL import Image
from rembg import new_session, remove


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--model", default="isnet-general-use")
    a = ap.parse_args()

    img = Image.open(a.src).convert("RGBA")
    out = remove(img, session=new_session(a.model), post_process_mask=True)
    bbox = out.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bbox:
        raise SystemExit("제품을 찾지 못했습니다. 배경이 단순한 제품 사진을 넣어 주세요.")
    out = out.crop(bbox)
    pad = int(max(out.size) * 0.02)
    canvas = Image.new("RGBA", (out.width + pad * 2, out.height + pad * 2), (0, 0, 0, 0))
    canvas.paste(out, (pad, pad), out)
    pathlib.Path(a.dst).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(a.dst)
    print(f"{a.dst} {canvas.width}x{canvas.height}")


if __name__ == "__main__":
    main()
