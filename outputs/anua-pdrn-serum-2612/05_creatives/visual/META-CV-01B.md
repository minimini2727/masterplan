# META-CV-01B 이미지 디자인 가이드

- 프로젝트: anua-pdrn-serum-2612
- 작성: 4번 팀원 / 광고 소재 제작자
- 작성일: 2026-11-01
- 참조 문서: `04_creative_brief.md`(2·5·6장), `03_media_mix.md`(6·7장 UTM·규격), `02_strategy.md`(6장 메시지 축), `team/STANDARDS.md`
- 데이터 한계: 가격·할인율·구성·리뷰 수·어워즈는 미확정이라 `[확정 후 기입: 항목]` 플레이스홀더로 둔다. 글자 수는 Bash(python3 len, 공백·줄바꿈 포함)로 계산했고, 플레이스홀더는 "고정 글자 수"와 "가정 값 기입 시 글자 수"(할인율 3자 예: 40%, 세일가 7자 예: 19,900원, 구성 12자, 리뷰 수 5자, 기준일 10자)를 함께 적었다. GFA·카카오 비즈보드 글자 수, YouTube·Meta 일부 사양은 `[확인 필요]`(운영 대행팀 11-14 확인).

## 개요
| 항목 | 내용 |
|---|---|
| 매체/규격 | Meta 협력광고 판매 4:5, 1080x1350, JPG/PNG |
| 컨셉 | C1 캡슐 텍스처 |
| 카피 | `copy/META-CV-01B.md` |
| 파일명 | META-CV-01B_texture_45i_v1.jpg |

## 레이아웃
| 영역 | 위치·크기(px) | 내용 | 스타일 |
|---|---|---|---|
| 제목 | x 65~1015, y 90~200 | 톡 터지는 PDRN 캡슐 세럼 | Paperlogy Bold 64px #2B2B2B, 가운데 정렬 |
| 키 비주얼 | x 0~1080, y 230~980 | 손등 위 캡슐이 손끝에 눌려 터지는 순간 매크로(물방울 튀는 정지 컷) | 화면 중앙, 캡슐 지름 약 260px |
| 제품 | x 700~1000, y 640~1100 | 제품 병 누끼, 45도 | 그림자 #2B2B2B 15% 블러 30px |
| 혜택 | x 65~1015, y 1110~1200 | 올영세일 [확정 후 기입: 할인율] · 12/1~12/6 | 코랄레드 #E8384F 라운드 박스(r 16) 안 흰 글자 48px |
| 고지 | x 65~1015, y 1230~1300 | 올영세일 기간 2026-12-01~2026-12-06, 올리브영 온라인몰 기준, 구성·가격은 행사에 따라 달라질 수 있음 | Paperlogy Regular 22px #6B6B6B, 2줄 허용 |
| 로고 | x 900~1015, y 30~80 | ANUA | 흑백 로고 |

## 컬러 `[가정: 브랜드 가이드 미제공, 기획서 1장 "밝고 깨끗한 겨울 톤"]`
| 용도 | 색 | HEX |
|---|---|---|
| 배경 기본 | 아이보리 | #FBF8F5 |
| 배경 포인트 | 연핑크 | #F8E1E7 |
| 투명 질감 하이라이트 | 아이시 블루 | #DDEFF5 |
| 본문 텍스트 | 차콜 | #2B2B2B |
| 보조·고지 텍스트 | 그레이 | #6B6B6B |
| 세일·마감 레이어 | 코랄레드 | #E8384F |

## 폰트
- 제목·혜택: Paperlogy Bold / 본문·고지: Paperlogy Regular (시안 HTML 지정 폰트, 상업 이용 라이선스는 브랜드 담당자 확인). 브랜드 전용 서체가 있으면 브랜드 담당자가 11-07까지 전달하고 교체한다.
- 숫자(할인율·세일가)는 Paperlogy ExtraBold, 같은 줄 한글보다 1.2배 크게.

## 이미지 생성 AI 프롬프트
- 생성형 AI는 **배경·텍스처·소품 컷**에만 쓴다. 제품 병은 실제 패키지 누끼(브랜드 제공)를 합성한다. AI가 만든 가짜 라벨·로고는 쓰지 않는다(표시광고 오인 방지).
- 권장 도구: Midjourney v7 / Firefly Image / Imagen 계열 `[가정]`. 상업 이용 약관을 브랜드 담당자가 확인한다.

**한국어**
```
흰 아크릴 배경 위 여성의 손등 클로즈업, 투명한 젤 캡슐 하나가 손끝에 눌려 톡 터지는 순간, 맑은 세럼 방울이 피부 표면 위로 살짝 튐, 확산광 소프트박스, 아이보리와 연핑크 톤, 매크로 100mm, 얕은 심도, 깨끗한 겨울 스킨케어 광고 사진, 세로 4:5
```

**English**
```
Macro close-up of the back of a hand on a white acrylic surface, a single clear gel capsule bursting under a fingertip, tiny droplets of clear serum splashing on the skin surface only, soft diffused light, ivory and pale pink palette, 100mm macro, shallow depth of field, clean winter skincare advertising photography, vertical 4:5 --ar 4:5 --style raw
```

**네거티브(공통)**
- KO: 주사기, 바늘, 실험실, 가운, 피부 단면, 피부 속으로 들어가는 그래픽, 전후 비교 분할 화면, 가짜 로고·라벨 글자, 과한 보정
- EN: `syringe, needle, lab coat, laboratory, skin cross-section, particles penetrating skin, before-and-after split, text, fake logo, fake label, watermark, oversaturated, plastic skin`

## 촬영·소스 목록
| 소스 | 사양 | 담당·일정 |
|---|---|---|
| 손등 캡슐 터지는 순간 스틸 | 4K 영상 100fps에서 프레임 추출 또는 고속 스틸 촬영, 100mm 매크로 | 촬영감독, 11-10 |
| 제품 병 누끼 | PNG 투명 4000px 이상, 정면·45도 2종 | 브랜드 담당자, 11-07 |
| 배경 | AI 생성(아래 프롬프트) 또는 흰 아크릴 촬영 | 디자이너 |

## PSD 레이어 구성
1. `BG` 배경(AI 생성 또는 촬영) 2. `PRODUCT` 제품 누끼 3. `KEY_VISUAL` 캡슐·윤기 컷 4. `TXT_TITLE` 제목 5. `TXT_OFFER` 혜택(할인율·세일가·기간, **확정 후 기입 레이어**) 6. `TXT_NOTICE` 고지 7. `LOGO` ANUA 로고
- 출력: JPG 품질 90, sRGB, 30MB 이하(Meta) / 파일명은 소재 ID + utm_content

## 금지 연출 체크 (기획서 6장)
- [x] 캡슐은 피부 표면 위에서만 터지고 펴 발림. 피부 속 침투 그래픽·피부 단면 없음
- [x] 주사기·바늘·가운·실험실·병원 소품 없음, 사용 전후 비교·분할 비교 없음
- [x] 이미지 텍스트에 기능성 미확인 효능·의약품 오인·시술 연상·최상급·함량 수치 표현 없음
- [x] 가격·할인율·기간은 별도 텍스트 레이어(확정 전 이미지에 박지 않음)

## 다음 담당자에게
- 디자이너: 11-12 1차 시안(가격 레이어 비움) → 11-18 확정값 반영 → 11-20 6번 검수.
- 브랜드 담당자: 제품 누끼(PNG 4000px), ANUA 로고 벡터를 11-07까지 전달.
