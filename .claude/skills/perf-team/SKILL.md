---
name: perf-team
description: 퍼포먼스 마케팅 팀(6명 서브에이전트)을 순서대로 돌려 브리프에서 팩트북, 전략, 미디어 믹스, 소재 기획, 소재 제작, 검수까지 끝내는 워크플로. "퍼포먼스 팀 돌려줘", "캠페인 기획해줘", "/perf-team <프로젝트명>" 요청 시 사용.
---

# 퍼포먼스 마케팅 팀 워크플로

당신은 이 팀의 **리드(오케스트레이터)**다. 직접 산출물을 쓰지 말고, 아래 서브에이전트에게 순서대로 일을 맡기고 결과를 연결한다.

| 번호 | 서브에이전트 | 역할 | 산출물 |
|---|---|---|---|
| 5 | `pm-researcher` | 팩트북 리서치 | `01_factbook.md` |
| 1 | `pm-strategist` | 전략 | `02_strategy.md` |
| 2 | `pm-media-planner` | 미디어 믹스 | `03_media_mix.md/.csv` |
| 3 | `pm-creative-planner` | 소재 기획 | `04_creative_brief.md` |
| 4 | `pm-creative-producer` | 소재 제작 | `05_creatives/` |
| 6 | `pm-qa-reviewer` | 검수 | `06_qa_report.md` |

공통 기준은 `team/STANDARDS.md`에 있다.

## 0단계. 브리프 확보
1. 프로젝트명을 정한다 (인자로 받았으면 사용, 영문·숫자·하이픈 권장).
2. `outputs/<프로젝트>/00_brief.md`가 없으면 `team/templates/brief.md`를 복사해 사용자가 준 정보로 채운다.
3. **최소 필수 항목**(제품, 목표 KPI, 총예산, 기간) 중 빠진 것이 있으면 AskUserQuestion으로 한 번에 묻는다. 나머지 빈칸은 팀원들이 `[가정]`으로 채운다.

## 1~6단계. 순서대로 실행
각 단계는 Agent 도구로 해당 서브에이전트를 호출한다. 프롬프트에는 항상 다음을 넣는다.
- 프로젝트 폴더 경로 (`outputs/<프로젝트>/`)
- 읽어야 할 앞 단계 파일
- 이전 단계가 반환한 요약과 미확정 항목

순서와 관문:
1. **pm-researcher** → 팩트북. 반환된 "신뢰도 낮은 항목"을 기록해 둔다.
2. **pm-strategist** → 전략서. `추가 조사 요청`이 있으면 pm-researcher를 다시 불러 보강한 뒤 전략가에게 반영을 요청한다.
3. **중간 검수 ①** pm-qa-reviewer에게 `01`, `02`만 검수시킨다 (특히 역산표 계산, 출처). `치명` 이슈가 있으면 전략가에게 수정시키고 다음으로 넘어간다.
4. **pm-media-planner** → 미디어 믹스.
5. **중간 검수 ②** pm-qa-reviewer에게 `03` 예산 합계·계산·상품 사양을 검수시킨다. `치명` 이슈는 수정 후 진행.
6. **pm-creative-planner** → 소재 기획서.
7. **pm-creative-producer** → 제작물. 소재가 많으면 우선순위 높은 것부터 만들게 한다.
   - 제작자가 `imagegen/*.json`을 쓰면 리드가 `python3 team/tools/gen_images.py outputs/<프로젝트>`로 gpt-image-2 실제 이미지를 만든다 (필요: `OPENAI_API_KEY`, 허용 도메인 `api.openai.com`). 먼저 우선순위 소재 2~3개로 시험 생성하고 PNG를 열어 확인한 뒤 나머지를 만든다.
   - **제품 누끼:** 제품 사진은 ① 사용자가 준 사진(`05_creatives/ref/source/`) ② 브랜드 공식몰·공식 보도자료 이미지 순으로 구한다. 아무 소매몰·블로그 이미지는 쓰지 않는다. 받은 파일은 새 빈 폴더에 두고 출처 URL과 받은 날짜를 `ref/SOURCES.md`에 적는다.
     `python3 -I team/tools/cutout.py <원본> outputs/<프로젝트>/05_creatives/ref/product_cutout.png` → `python3 team/tools/place_product.py outputs/<프로젝트>/05_creatives/banner outputs/<프로젝트>/05_creatives/ref/product_cutout.png` → PNG 다시 추출.
     누끼 결과는 PNG를 열어 가장자리·잘린 부분을 확인한다. 공식 원본이 아닌 이미지는 '시안용, 집행 전 브랜드 원본으로 교체'로 표시한다.
   - 키나 네트워크가 없으면 이미지 없이 시안을 만들고, 사용자에게 무엇이 막혔는지 알린다. 가짜 이미지로 채우지 않는다.
8. **최종 검수** pm-qa-reviewer에게 전체 검수를 시킨다.
9. 판정이 `반려`이거나 `치명`/`중요` 이슈가 있으면 담당 팀원에게 이슈 ID를 넘겨 수정시키고, 검수자에게 재검수시킨다. **수정-재검수는 최대 2회**까지 하고, 남은 이슈는 사용자에게 그대로 보고한다.

독립적인 작업은 병렬로 돌려도 된다 (예: 소재 제작 중 리서처의 추가 조사).

## 산출물 내보내기 (필수, 매번)
사용자 요청: **전략서는 PDF(페이퍼로지 폰트), 미디어 믹스는 엑셀**로 항상 전달한다. 파일은 `outputs/<프로젝트>/export/`에 만든다.
1. 전략서 PDF: 전략서가 완료(또는 수정)되면
   `python3 team/tools/md_to_pdf.py outputs/<프로젝트>/02_strategy.md "outputs/<프로젝트>/export/02_전략서_<프로젝트>.pdf" "<문서 제목>"`
   - 폰트는 `team/assets/fonts/Paperlogy-*.woff2`를 쓴다. `pdffonts`로 Paperlogy가 포함됐는지 확인한다.
2. 미디어 믹스 엑셀: 미디어 믹스가 완료(또는 수정)되면
   `python3 team/tools/media_mix_to_xlsx.py outputs/<프로젝트> "outputs/<프로젝트>/export/03_미디어믹스_<프로젝트>.xlsx" <객단가>`
   - 이어서 xlsx 스킬의 `recalc.py`로 재계산하고 `errors_found`가 없는지 확인한다.
3. 소재 PNG: 4번 제작자는 모든 소재 ID마다 `05_creatives/banner/<ID>.html`(실제 사양 크기, 폰트 'Paperlogy', 외부 리소스 없음)을 만든다. 리드는
   `node team/tools/html_to_png.js outputs/<프로젝트>/05_creatives/banner outputs/<프로젝트>/export/creatives_png`
   로 PNG를 만들고 몇 장을 열어 확인한 뒤 zip으로 묶는다.
4. 결과물 링크(마지막에 항상): 페이지 설정 json(제목, 요약 KPI, 매체 표, 검수 판정, 런칭 전 확인 사항, 저장소 URL)을 만들고
   `python3 team/tools/build_delivery_page.py outputs/<프로젝트> <설정.json>` → `export/index.html`.
   Artifact로 publish한다(`root`=export 폴더, `files`=PDF·`b64/*.txt`·`creatives_png/*.png`, `capabilities: {downloads: true}`). xlsx·zip은 Artifact에 직접 못 올리므로 b64 텍스트로 올리고 페이지가 원래 파일로 복원해 저장한다. 링크를 최종 보고 맨 끝에 준다.
5. 위 파일들을 SendUserFile로 사용자에게 보낸다. 최종 검수 후 수정이 생기면 다시 만들어 다시 보낸다.

## 마무리 보고 (사용자에게)
- 최종 KPI와 기본 시나리오 예산·예상 성과 범위
- 매체별 예산 요약 표
- 제작된 소재 수와 우선 집행 소재
- 검수 판정과 남은 이슈 (해결 못 한 것은 숨기지 말고 명시)
- 런칭 전 사용자가 직접 해야 할 일 (계정·픽셀 세팅, 소재 실물 제작, 법무 확인 등)과 담당·일정
- 산출물 파일 목록

## 일부 단계만 요청할 때
사용자가 특정 단계만 원하면 (예: "미디어 믹스만 다시"), 해당 서브에이전트와 검수자만 호출한다. 앞 단계 파일이 없으면 무엇이 부족한지 알리고, 브리프 기반 `[가정]`으로 진행할지 묻는다.
