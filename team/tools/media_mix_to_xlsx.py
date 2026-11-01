#!/usr/bin/env python3
"""미디어 믹스(03_media_mix.csv + 03_media_mix.md)를 엑셀로 변환한다.

사용법: python3 team/tools/media_mix_to_xlsx.py <프로젝트 폴더> <출력.xlsx> [객단가(원)]

시트 구성
- 기본 시나리오: csv 행. 예산·노출·클릭·전환은 입력값(파란 글씨), 비중·CPM·CTR·CPC·CVR·CPA·매출·ROAS는 수식.
- 요약: 총예산, 측정 가능 매체 예산/매출/ROAS 등 핵심 지표(수식).
- 그 외: 03_media_mix.md의 모든 표를 소제목 이름의 시트로 옮긴다(값 그대로, 숫자는 숫자로 변환).
"""
import csv
import pathlib
import re
import sys

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

FONT = "맑은 고딕"
BLUE = "0000FF"
HEAD_FILL = PatternFill("solid", fgColor="2F5D50")
TOTAL_FILL = PatternFill("solid", fgColor="EEF2F0")
INPUT_FILL = PatternFill("solid", fgColor="FFFF00")
THIN = Side(style="thin", color="D9D9DE")
BORDER = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)
WON = '#,##0;(#,##0);"-"'
PCT = '0.00%;(0.00%);"-"'


def f(bold=False, color="000000", size=10):
    return Font(name=FONT, bold=bold, color=color, size=size)


def style_header(ws, row, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = f(True, "FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = BORDER


def to_number(text):
    t = text.replace("**", "").replace("원", "").replace(",", "").strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", t):
        return float(t) if "." in t else int(t)
    return None


def build_main(wb, rows, aov):
    ws = wb.active
    ws.title = "기본 시나리오"
    ws["A1"] = "기본 시나리오 미디어 믹스 (금액 단위: 원, VAT 별도)"
    ws["A1"].font = f(True, size=13)
    ws["A2"] = "객단가(원)"
    ws["B2"] = aov
    ws["B2"].font = f(color=BLUE)
    ws["B2"].fill = INPUT_FILL
    ws["B2"].number_format = WON
    ws["B2"].comment = Comment("[가정] 전략서 2-3 객단가. 실판매가 확정 시 이 칸만 바꾸면 매출·ROAS가 다시 계산됩니다.", "pm-team")
    ws["C2"] = "← 노란 칸, 파란 글씨 = 입력값(가정). 검정 = 수식"
    ws["C2"].font = f(color="6B6B70", size=9)

    headers = ["매체", "광고 상품", "퍼널", "캠페인 목표", "타겟팅", "입찰/과금", "기간",
               "예산", "비중", "예상 노출", "예상 클릭", "예상 전환", "매출 측정",
               "CPM", "CTR", "CPC", "CVR", "CPA", "예상 매출", "ROAS", "근거"]
    hr = 4
    for i, h in enumerate(headers, 1):
        ws.cell(row=hr, column=i, value=h)
    style_header(ws, hr, len(headers))

    first = hr + 1
    for r_i, r in enumerate(rows):
        r_n = first + r_i
        measured = "구매 측정" if r["예상 전환"].strip() else "유입 지표만"
        vals = [r["매체"], r["광고 상품"], r["퍼널"], r["캠페인 목표"], r["타겟팅"], r["입찰/과금"], r["기간"]]
        for c, v in enumerate(vals, 1):
            ws.cell(row=r_n, column=c, value=v)
        for c, key in zip((8, 10, 11, 12), ("예산", "예상 노출", "예상 클릭", "예상 전환")):
            num = to_number(r[key]) if r[key].strip() else None
            cell = ws.cell(row=r_n, column=c, value=num)
            cell.font = f(color=BLUE)
            cell.number_format = WON
        ws.cell(row=r_n, column=13, value=measured)
        L = r_n
        tot = f"$H${first + len(rows)}"
        ws.cell(row=L, column=9, value=f"=IFERROR(H{L}/{tot},0)").number_format = PCT
        ws.cell(row=L, column=14, value=f'=IFERROR(H{L}/J{L}*1000,"-")').number_format = WON
        ws.cell(row=L, column=15, value=f'=IFERROR(K{L}/J{L},"-")').number_format = PCT
        ws.cell(row=L, column=16, value=f'=IFERROR(H{L}/K{L},"-")').number_format = WON
        ws.cell(row=L, column=17, value=f'=IF(L{L}="","-",IFERROR(L{L}/K{L},"-"))').number_format = PCT
        ws.cell(row=L, column=18, value=f'=IF(L{L}="","-",IFERROR(H{L}/L{L},"-"))').number_format = WON
        ws.cell(row=L, column=19, value=f'=IF(L{L}="","-",L{L}*$B$2)').number_format = WON
        ws.cell(row=L, column=20, value=f'=IF(L{L}="","-",IFERROR(S{L}/H{L},"-"))').number_format = PCT
        ws.cell(row=L, column=21, value=r.get("근거", ""))

    last = first + len(rows) - 1
    t = last + 1
    ws.cell(row=t, column=1, value="합계")
    for c in (8, 10, 11, 12, 19):
        col = get_column_letter(c)
        ws.cell(row=t, column=c, value=f"=SUM({col}{first}:{col}{last})").number_format = WON
    ws.cell(row=t, column=9, value=f"=SUM(I{first}:I{last})").number_format = PCT
    ws.cell(row=t, column=13, value="측정 매체 ROAS →")
    ws.cell(row=t, column=20, value=(f'=IFERROR(SUMIFS(S{first}:S{last},M{first}:M{last},"구매 측정")'
                                    f'/SUMIFS(H{first}:H{last},M{first}:M{last},"구매 측정"),0)')).number_format = PCT
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=t, column=c)
        cell.font = f(True)
        cell.fill = TOTAL_FILL

    for row in ws.iter_rows(min_row=first, max_row=t, max_col=len(headers)):
        for cell in row:
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if cell.font.color is None or cell.font.color.rgb not in ("FF" + BLUE, BLUE):
                cell.font = f(cell.font.bold)
    widths = [14, 28, 8, 16, 34, 20, 22, 13, 8, 12, 10, 9, 11, 9, 8, 9, 8, 9, 13, 9, 60]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=first, column=3)
    ws.cell(row=t + 2, column=1, value=("주: 예상 매출 = 예상 전환 × 객단가. csv의 전환 수는 반올림 값이라 "
                                       "문서의 측정 매출과 수천~수만 원 차이가 날 수 있습니다. 대부분의 입력값은 [가정]이며 근거 열을 참고하세요."))
    ws.cell(row=t + 2, column=1).font = f(color="6B6B70", size=9)
    return ws, first, last, t


def build_summary(wb, first, last, t):
    ws = wb.create_sheet("요약", 0)
    S = "'기본 시나리오'!"
    ws["A1"] = "미디어 믹스 요약 (기본 시나리오, 원, VAT 별도)"
    ws["A1"].font = f(True, size=13)
    rng = lambda col: f"{S}{col}{first}:{col}{last}"
    items = [
        ("총예산", f"={S}H{t}", WON),
        ("매출 측정 매체 예산", f'=SUMIFS({rng("H")},{rng("M")},"구매 측정")', WON),
        ("매출 측정 매체 비중", "=IFERROR(B4/B3,0)", PCT),
        ("유입 지표만 보는 매체 예산", f'=SUMIFS({rng("H")},{rng("M")},"유입 지표만")', WON),
        ("예상 구매 수", f"={S}L{t}", WON),
        ("예상 측정 매출", f"={S}S{t}", WON),
        ("측정 ROAS (측정 매체 기준)", f"={S}T{t}", PCT),
        ("총예산 대비 측정 매출", "=IFERROR(B8/B3,0)", PCT),
        ("객단가 (입력은 기본 시나리오 B2)", f"={S}B2", WON),
    ]
    ws["A2"], ws["B2"] = "지표", "값"
    style_header(ws, 2, 2)
    for i, (k, formula, fmt) in enumerate(items, 3):
        ws.cell(row=i, column=1, value=k).font = f()
        c = ws.cell(row=i, column=2, value=formula)
        c.font = f(color="008000")
        c.number_format = fmt
        for col in (1, 2):
            ws.cell(row=i, column=col).border = BORDER
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 18
    ws.cell(row=len(items) + 4, column=1, value="잠정 목표: 측정 ROAS 250% 이상 (11-14 실측 후 재설정). 세부 근거는 02_strategy.md, 03_media_mix.md 참고.").font = f(color="6B6B70", size=9)


def md_tables(md_text):
    """(소제목, 표 행 목록) 을 순서대로 돌려준다."""
    heading, buf, out = "표", [], []
    for line in md_text.splitlines() + [""]:
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
        if line.lstrip().startswith("|"):
            buf.append(line.strip())
            continue
        if buf:
            rows = [[c.strip() for c in b.strip("|").split("|")] for b in buf
                    if not re.fullmatch(r"\|?[\s:\-|]+\|?", b)]
            out.append((heading, rows))
            buf = []
    return out


def safe_title(name, used):
    name = re.sub(r"\s*\(.*$", "", name)  # 괄호 이후 설명은 시트 이름에서 뺀다
    name = re.sub(r"[\[\]\:\*\?\/\\]", "", name).strip() or "표"
    name = name[:28]
    base, n = name, 2
    while name in used:
        name = f"{base[:25]}_{n}"
        n += 1
    used.add(name)
    return name


def build_md_sheets(wb, md_text):
    used = set(wb.sheetnames)
    for heading, rows in md_tables(md_text):
        ws = wb.create_sheet(safe_title(heading, used))
        ws["A1"] = heading
        ws["A1"].font = f(True, size=12)
        for r_i, row in enumerate(rows, 3):
            for c_i, v in enumerate(row, 1):
                num = to_number(v)
                text = v.replace("**", "").replace("`", "")
                cell = ws.cell(row=r_i, column=c_i, value=num if num is not None else text)
                cell.font = f(r_i == 3 or v.startswith("**"))
                cell.border = BORDER
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                if num is not None:
                    cell.number_format = WON if isinstance(num, int) else "0.00"
        style_header(ws, 3, len(rows[0]))
        for c_i in range(1, len(rows[0]) + 1):
            longest = max(len(str(r[c_i - 1])) if c_i - 1 < len(r) else 0 for r in rows)
            ws.column_dimensions[get_column_letter(c_i)].width = min(max(10, longest * 1.3), 60)
        ws.freeze_panes = "A4"


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    proj = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    aov = int(sys.argv[3]) if len(sys.argv) > 3 else 30000
    with open(proj / "03_media_mix.csv", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    wb = Workbook()
    _, first, last, t = build_main(wb, rows, aov)
    build_summary(wb, first, last, t)
    md = proj / "03_media_mix.md"
    if md.exists():
        build_md_sheets(wb, md.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(out)


if __name__ == "__main__":
    main()
