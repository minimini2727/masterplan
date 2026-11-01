#!/usr/bin/env python3
"""OpenAI gpt-image-2로 광고 소재용 실제 이미지를 만든다.

사용법:
  python3 team/tools/gen_images.py <프로젝트 폴더> [--only ID1,ID2] [--quality low|medium|high] [--dry-run] [--force]

입력: <프로젝트>/05_creatives/imagegen/<소재ID>.json  (4번 제작자가 작성)
  {
    "size": "1080x1350",              # 최종 소재 크기(사양 그대로)
    "prompt": "영문 프롬프트 ...",      # 이미지 안에 글자 넣지 말 것(카피는 HTML에서 얹는다)
    "reference": "assets/ref/product.png",   # 선택: 실제 제품 사진(있으면 edits 엔드포인트로 제품을 유지)
    "quality": "medium"               # 선택
  }
출력: <프로젝트>/05_creatives/assets/<소재ID>.png  (사양 크기로 정확히 잘라 맞춤)
      <프로젝트>/05_creatives/assets/_log.csv     (ID, 요청 크기, 품질, 결과)

필요: 환경변수 OPENAI_API_KEY, 네트워크 허용 도메인 api.openai.com
모델: gpt-image-2 (OpenAI 모델 페이지 기준 2026-04-21 스냅샷). 크기는 16의 배수, 긴 변 3840px 미만.
"""
import argparse
import base64
import csv
import io
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

API = "https://api.openai.com/v1/images"
MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
MAX_EDGE = 3824  # 3840 미만, 16의 배수


def gen_size(w, h):
    """사양 비율을 유지하면서 16의 배수로 올린 생성 크기.
    작은 사양은 약 1.57MP(1024x1536 수준)까지 키우고, 큰 사양은 그대로 둔다(긴 변 3840 미만)."""
    scale = max(1.0, (1024 * 1536 / (w * h)) ** 0.5)
    gw, gh = w * scale, h * scale
    if max(gw, gh) > MAX_EDGE:
        r = MAX_EDGE / max(gw, gh)
        gw, gh = gw * r, gh * r
    up = lambda v: int(-(-v // 16) * 16)
    return min(up(gw), MAX_EDGE), min(up(gh), MAX_EDGE)


def fit_exact(img, w, h):
    """가운데 기준으로 비율을 맞춰 자른 뒤 정확한 사양 크기로 줄인다."""
    iw, ih = img.size
    target = w / h
    if iw / ih > target:
        nw = int(ih * target)
        img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / target)
        img = img.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    return img.resize((w, h), Image.LANCZOS)


def multipart(fields, files):
    boundary = "----pmteam" + str(int(time.time() * 1000))
    body = io.BytesIO()
    for k, v in fields.items():
        body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, path in files:
        data = pathlib.Path(path).read_bytes()
        body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{pathlib.Path(path).name}"\r\n'
                   f"Content-Type: image/png\r\n\r\n".encode() + data + b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())
    return body.getvalue(), f"multipart/form-data; boundary={boundary}"


def call(spec, size, quality, key, base_dir):
    ref = spec.get("reference")
    if ref:
        body, ctype = multipart(
            {"model": MODEL, "prompt": spec["prompt"], "size": size, "quality": quality, "n": "1"},
            [("image[]", base_dir / ref)])
        url = f"{API}/edits"
    else:
        body = json.dumps({"model": MODEL, "prompt": spec["prompt"], "size": size,
                           "quality": quality, "n": 1}).encode()
        ctype = "application/json"
        url = f"{API}/generations"
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": ctype})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read())
            return base64.b64decode(data["data"][0]["b64_json"])
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** (attempt + 2))
                continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--only", default="")
    ap.add_argument("--quality", default="medium", choices=["low", "medium", "high"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="이미 있는 이미지도 다시 생성")
    a = ap.parse_args()

    base = pathlib.Path(a.project) / "05_creatives"
    specs = sorted((base / "imagegen").glob("*.json"))
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    if only:
        specs = [s for s in specs if s.stem in only]
    if not specs:
        sys.exit("imagegen/*.json 이 없습니다. 4번 제작자가 소재별 이미지 사양을 먼저 작성해야 합니다.")
    key = os.environ.get("OPENAI_API_KEY")
    if not key and not a.dry_run:
        sys.exit("OPENAI_API_KEY 환경변수가 없습니다. 클라우드 환경 설정에 키를 추가한 뒤 새 세션에서 실행하세요. (--dry-run으로 계획만 확인 가능)")

    out = base / "assets"
    out.mkdir(exist_ok=True)
    log_rows, ok, fail = [], 0, 0
    for p in specs:
        spec = json.loads(p.read_text(encoding="utf-8"))
        w, h = map(int, spec["size"].lower().split("x"))
        gw, gh = gen_size(w, h)
        q = spec.get("quality", a.quality)
        dst = out / f"{p.stem}.png"
        if dst.exists() and not a.force:
            log_rows.append([p.stem, f"{gw}x{gh}", q, "건너뜀(이미 있음)"])
            continue
        if a.dry_run:
            print(f"[계획] {p.stem}: 생성 {gw}x{gh} → 최종 {w}x{h}, 품질 {q}, 참조 {spec.get('reference', '없음')}")
            continue
        try:
            raw = call(spec, f"{gw}x{gh}", q, key, base)
            fit_exact(Image.open(io.BytesIO(raw)).convert("RGB"), w, h).save(dst)
            ok += 1
            log_rows.append([p.stem, f"{gw}x{gh}", q, "성공"])
            print(f"[성공] {p.stem} → {dst}")
        except Exception as e:  # 실패해도 나머지는 계속 만든다
            fail += 1
            log_rows.append([p.stem, f"{gw}x{gh}", q, f"실패: {e}"])
            print(f"[실패] {p.stem}: {e}", file=sys.stderr)
    if not a.dry_run:
        with open(out / "_log.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(log_rows)
        print(f"성공 {ok} / 실패 {fail} / 전체 {len(specs)}")


if __name__ == "__main__":
    main()
