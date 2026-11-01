#!/usr/bin/env python3
"""프로젝트 export 폴더로 결과물 다운로드·미리보기 페이지(HTML)를 만든다.

사용법: python3 team/tools/build_delivery_page.py <프로젝트 폴더> <페이지 설정 json>
출력: <프로젝트>/export/index.html  (Artifact로 publish, files에 export 하위 파일 포함)

설정 json 예시: {"title": "...", "subtitle": "...", "summary": [["라벨","값","설명"]...],
  "media": [["매체","예산","비중","측정"]...], "qa": "...", "todo": [["할 일","담당","기한"]...],
  "repo_url": "https://github.com/..."}
"""
import html
import json
import pathlib
import sys

from PIL import Image

GROUPS = [
    ("META-CV", "Meta 협력광고 · 판매"), ("META-RT", "Meta 협력광고 · 리타겟"),
    ("META-AW", "Meta 인지"), ("YT", "YouTube"), ("GFA", "네이버 GFA"),
    ("PL", "네이버 파워링크"), ("KKO", "카카오 비즈보드"),
]


def esc(s):
    return html.escape(str(s))


def main():
    proj = pathlib.Path(sys.argv[1])
    cfg = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
    exp = proj / "export"
    pngs = sorted((exp / "creatives_png").glob("*.png"))
    files = [p for p in sorted(exp.iterdir()) if p.is_file() and p.suffix in (".pdf", ".xlsx", ".zip")]
    kinds = {".pdf": ("PDF", "전략서"), ".xlsx": ("XLSX", "미디어 믹스"), ".zip": ("ZIP", "소재 시안 PNG")}

    dl_cards = []
    for p in files:
        k, label = kinds[p.suffix]
        size = p.stat().st_size
        size_s = f"{size/1024/1024:.1f}MB" if size > 1024 * 1024 else f"{size/1024:.0f}KB"
        dl_cards.append(
            f'<li class="dl"><span class="ext">{k}</span><div class="dl-body"><strong>{esc(label)}</strong>'
            f'<span class="fname">{esc(p.name)}</span></div><span class="size">{size_s}</span>'
            f'<button type="button" class="btn" data-file="{esc(p.name)}">받기</button></li>')

    sections = []
    used = set()
    for prefix, name in GROUPS:
        items = [p for p in pngs if p.stem.startswith(prefix) and p not in used]
        used.update(items)
        if not items:
            continue
        tiles = []
        for p in items:
            w, h = Image.open(p).size
            rel = f"creatives_png/{p.name}"
            tiles.append(
                f'<figure class="tile"><div class="frame" style="aspect-ratio:{w}/{h}">'
                f'<img src="{rel}" alt="{esc(p.stem)} 시안" loading="lazy"></div>'
                f'<figcaption><span>{esc(p.stem)}</span><span class="dim">{w}×{h}</span>'
                f'<button type="button" class="link" data-file="{rel}">PNG</button></figcaption></figure>')
        sections.append(f'<section class="group"><h3>{esc(name)} <span class="count">{len(items)}</span></h3>'
                        f'<div class="grid">{"".join(tiles)}</div></section>')

    summary = "".join(f'<div class="kpi"><span class="k-label">{esc(a)}</span><span class="k-val">{esc(b)}</span>'
                      f'<span class="k-note">{esc(c)}</span></div>' for a, b, c in cfg["summary"])
    media = "".join(f"<tr><td>{esc(a)}</td><td class='num'>{esc(b)}</td><td class='num'>{esc(c)}</td>"
                    f"<td><span class='tag {'on' if d == '구매 측정' else 'off'}'>{esc(d)}</span></td></tr>"
                    for a, b, c, d in cfg["media"])
    todo = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td class='num'>{esc(c)}</td></tr>" for a, b, c in cfg["todo"])

    page = TEMPLATE.format(
        title=esc(cfg["title"]), subtitle=esc(cfg["subtitle"]), downloads="".join(dl_cards),
        summary=summary, media=media, qa=esc(cfg["qa"]), todo=todo, gallery="".join(sections),
        n=len(pngs), repo=esc(cfg.get("repo_url", "")))
    (exp / "index.html").write_text(page, encoding="utf-8")
    print(exp / "index.html", len(pngs), "png")


TEMPLATE = """<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
/* 레이아웃: 상단 내려받기 → 캠페인 요약 → 매체 표 → 확인 사항 → 소재 시안 갤러리. 캠페인 산출물 납품 시트 */
:root {{
  --bg:#f6f7f5; --surface:#ffffff; --fg:#1b1f1d; --muted:#5f6763; --line:#dde2df;
  --accent:#2f5d50; --accent-soft:#e3ece8; --warn:#9a5b13; --warn-soft:#f6ecdf; --frame:#eef0ee;
  --sans:'IBM Plex Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#121514; --surface:#1a1e1c; --fg:#e7ebe9; --muted:#9ba5a0; --line:#2c3330;
  --accent:#8cc4b0; --accent-soft:#203029; --warn:#e3b06e; --warn-soft:#2e2519; --frame:#232826; color-scheme:dark; }} }}
:root[data-theme="dark"] {{
  --bg:#121514; --surface:#1a1e1c; --fg:#e7ebe9; --muted:#9ba5a0; --line:#2c3330;
  --accent:#8cc4b0; --accent-soft:#203029; --warn:#e3b06e; --warn-soft:#2e2519; --frame:#232826; color-scheme:dark; }}
* {{ box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--sans); font-size:15px; line-height:1.6; word-break:keep-all; }}
.wrap {{ max-width:1120px; margin:0 auto; padding-block:40px 64px;
  padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px));
  display:flex; flex-direction:column; gap:40px; }}
header .eyebrow {{ font-family:var(--mono); font-size:12px; letter-spacing:.12em; color:var(--accent); text-transform:uppercase; }}
h1 {{ font-size:clamp(24px,4vw,34px); line-height:1.25; margin:8px 0 6px; font-weight:600; text-wrap:balance; }}
header p {{ margin:0; color:var(--muted); max-width:65ch; }}
h2 {{ font-size:18px; font-weight:600; margin:0 0 14px; text-wrap:balance; }}
h3 {{ font-size:15px; font-weight:600; margin:0 0 12px; display:flex; align-items:center; gap:8px; }}
.count {{ font-family:var(--mono); font-size:12px; color:var(--muted); background:var(--frame); padding:1px 8px; border-radius:99px; }}
.dls {{ list-style:none; margin:0; padding:0; display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr)); gap:12px; }}
.dl {{ display:flex; align-items:center; gap:14px; background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:14px 16px; min-width:0; }}
.ext {{ font-family:var(--mono); font-size:12px; color:var(--accent); background:var(--accent-soft); padding:6px 8px; border-radius:6px; }}
.dl-body {{ display:flex; flex-direction:column; min-width:0; flex:1; }}
.fname {{ font-size:12px; color:var(--muted); overflow-wrap:anywhere; }}
.size {{ font-family:var(--mono); font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums; }}
.btn {{ font:inherit; font-weight:600; font-size:14px; color:var(--bg); background:var(--accent); border:0; border-radius:8px; padding:8px 14px; cursor:pointer; }}
.btn:focus-visible, .link:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
.btn[disabled] {{ opacity:.5; cursor:default; }}
.status {{ min-height:1.4em; margin:10px 0 0; font-size:13px; color:var(--muted); }}
.kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr)); gap:12px; }}
.kpi {{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:14px 16px; display:flex; flex-direction:column; gap:2px; }}
.k-label {{ font-size:12px; color:var(--muted); }}
.k-val {{ font-size:22px; font-weight:600; font-variant-numeric:tabular-nums; }}
.k-note {{ font-size:12px; color:var(--muted); }}
.cols {{ display:grid; grid-template-columns:minmax(0,1.2fr) minmax(0,1fr); gap:24px; }}
@media (max-width:820px) {{ .cols {{ grid-template-columns:minmax(0,1fr); }} }}
.table-wrap {{ overflow-x:auto; background:var(--surface); border:1px solid var(--line); border-radius:10px; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th, td {{ text-align:left; padding:9px 12px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ font-size:12px; color:var(--muted); font-weight:500; }}
tr:last-child td {{ border-bottom:0; }}
.num {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
.tag {{ font-size:12px; padding:2px 8px; border-radius:99px; white-space:nowrap; }}
.tag.on {{ background:var(--accent-soft); color:var(--accent); }}
.tag.off {{ background:var(--frame); color:var(--muted); }}
.qa {{ background:var(--warn-soft); color:var(--fg); border-radius:10px; padding:14px 16px; margin:0 0 14px; font-size:14px; }}
.qa strong {{ color:var(--warn); }}
.note {{ font-size:13px; color:var(--muted); margin:8px 0 0; }}
.group + .group {{ margin-top:28px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,170px),1fr)); gap:14px; align-items:start; }}
.tile {{ margin:0; display:flex; flex-direction:column; gap:6px; min-width:0; }}
.frame {{ background:var(--frame); border:1px solid var(--line); border-radius:8px; overflow:hidden; display:flex; max-width:100%; max-height:320px; }}
.frame img {{ width:100%; height:100%; object-fit:contain; display:block; }}
figcaption {{ display:flex; align-items:center; gap:6px; font-family:var(--mono); font-size:11.5px; flex-wrap:wrap; }}
figcaption .dim {{ color:var(--muted); }}
.link {{ font:inherit; margin-left:auto; background:none; border:1px solid var(--line); color:var(--accent); border-radius:6px; padding:1px 7px; cursor:pointer; }}
footer {{ font-size:13px; color:var(--muted); border-top:1px solid var(--line); padding-top:16px; overflow-wrap:anywhere; }}
footer a {{ color:var(--accent); }}
</style>

<div class="wrap">
  <header>
    <div class="eyebrow">Performance Marketing · 결과물</div>
    <h1>{title}</h1>
    <p>{subtitle}</p>
  </header>

  <section aria-labelledby="dl-h">
    <h2 id="dl-h">내려받기</h2>
    <ul class="dls">{downloads}</ul>
    <p class="status" id="status" role="status"></p>
  </section>

  <section aria-labelledby="sum-h">
    <h2 id="sum-h">기본 시나리오 요약</h2>
    <div class="kpis">{summary}</div>
  </section>

  <div class="cols">
    <section aria-labelledby="mm-h">
      <h2 id="mm-h">매체별 예산 (원, VAT 별도)</h2>
      <div class="table-wrap"><table><thead><tr><th>매체 / 상품</th><th>예산</th><th>비중</th><th>매출 측정</th></tr></thead><tbody>{media}</tbody></table></div>
    </section>
    <section aria-labelledby="qa-h">
      <h2 id="qa-h">검수 결과와 런칭 전 확인</h2>
      <p class="qa">{qa}</p>
      <div class="table-wrap"><table><thead><tr><th>확인할 일</th><th>담당</th><th>기한</th></tr></thead><tbody>{todo}</tbody></table></div>
    </section>
  </div>

  <section aria-labelledby="g-h">
    <h2 id="g-h">소재 시안 {n}종</h2>
    <p class="note">레이아웃·카피 확인용 시안입니다. 회색 '제품 컷' 자리는 실제 촬영본으로, [확정 후 기입] 칸은 확정된 할인율·기간으로 바꿔 집행합니다.</p>
    {gallery}
  </section>

  <footer>원본 문서(마크다운, 소재 카피·콘티)는 GitHub 저장소에 있습니다: <a href="{repo}" target="_blank" rel="noopener">{repo}</a></footer>
</div>

<script>
(function () {{
  var statusEl = document.getElementById('status');
  var dlPromise = window.claude && window.claude.use ? window.claude.use('downloads') : Promise.resolve(null);
  function say(t) {{ statusEl.textContent = t; }}
  document.addEventListener('click', async function (e) {{
    var b = e.target.closest('[data-file]');
    if (!b) return;
    var path = b.getAttribute('data-file');
    var name = path.split('/').pop();
    var dl = await dlPromise;
    if (!dl) {{ say('이 화면에서는 내려받기를 쓸 수 없습니다. 아래 GitHub 저장소에서 받아 주세요.'); return; }}
    b.disabled = true;
    say(name + ' 준비 중…');
    try {{
      var res = await fetch(path);
      if (!res.ok) throw new Error('fetch');
      var blob = await res.blob();
      await dl.save({{ filename: name, data: blob }});
      say(name + ' 저장을 요청했습니다.');
    }} catch (err) {{
      var code = err && err.code;
      if (code === 'declined') say('저장을 취소했습니다.');
      else if (code === 'rate_limited') say('다른 저장 확인 창이 열려 있습니다. 잠시 후 다시 눌러 주세요.');
      else say(name + '을(를) 받지 못했습니다. GitHub 저장소에서 받아 주세요.');
    }} finally {{ b.disabled = false; }}
  }});
}})();
</script>
"""

if __name__ == "__main__":
    main()
