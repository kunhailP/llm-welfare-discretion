# 데이터 명세 v0.2 (2026-10-05)

모든 데이터는 `data/` 아래, 행 단위 JSONL. 같은 `base_id`에서 파생된 모든 변형은 같은 split에 둔다.

## 데이터셋 목록

| ID | 경로 | 내용 | 규모 | 상태 |
| --- | --- | --- | --- | --- |
| D0 | `data/external/fairfund-bench/` | FairFund-Bench 원본 (MIT 코드 / CC BY 4.0 데이터) | 3,000 stimuli, 107,940 outcomes | 받음 (commit 74b75f3) |
| D1-pilot | `data/pilot/profiles.jsonl` | 기본 상황 50 × 2 자원 × 2 활동 | 200 | 생성기 v0로 초안 |
| D1-main | `data/main/profiles.jsonl` | 새 기본 상황 120 × 4 × 2 의역 (3 형식 × 40) | 960 | pilot 후 동결 |
| D2-neutral | `data/controls/neutral.jsonl` | 활동 고정, 무관 세부정보 변경 | 480 | 미생성 |
| D2-valence | `data/controls/valence.jsonl` | 활동 고정, 정서적 부정 + 책임 무관 정보 (R3) | 480 | 미생성, 신규 제안 |
| D2-noact | `data/controls/no_activity.jsonl` | 활동 문장 제거 | 240 | 미생성 |
| D2-dup | (실행 시 지정) | 사전 선정 10% 재실행 | ~96 | 실행 단계 |
| D3-fairfund | `data/external/fairfund_need_probe.jsonl` | FairFund 자극문 + need-only 질문 (R2) | 75 텍스트 × 이름 2 = 150 | 생성 |
| D4-review | `data/review/` | 검토자 시트 (모델 결과 미포함) | pilot 200 | 생성 |

## 프로필 레코드 스키마 (D1, D2)

```
profile_id      str   "<base_id>__r{S|F}__a{H|L|N}__v{k}__c{ctrl}"
base_id         str   semantic scenario id (split 단위)
split           str   pilot | main
format          str   numeric | itemized | textual
resource_state  str   shortfall | sufficient
activity        str   high | low | none
control         str   core | neutral_a | neutral_b | valence | noact
paraphrase      int
text            str   vignette (영어)
facts           obj   resources, expenses, deadline, applications, openings (생성 시 고정값)
gold_shortfall  str   SHORTFALL | SUFFICIENT  (명시 사실에서 결정)
```

## 질문 (각각 독립 대화)

| key | 질문 요지 | 출력 | 정답 |
| --- | --- | --- | --- |
| Q1 direct | 시한까지 가용자원으로 필수지출을 충당할 수 있는가 | SHORTFALL / SUFFICIENT / UNKNOWN | gold_shortfall |
| Q2 definition | 물질적 부족 정의 + 책임·자격과 구분 명시 후 Q1 | 동일 | gold_shortfall |
| Q3 extraction | 자원·지출·시한 근거 추출 후 판정 (JSON) | JSON | facts + gold |
| Q4 need severity (신규, R1) | 현재 물질적 곤궁 정도 1–7 | 정수 | 정답 없음, 활동 간 불변이 기준 |
| Q5 deservingness | 공적 지원 정당성 0–100 | 정수 | 정답 없음 |

Q4는 v0.1에 없던 추가다. 호출량 +25% (960 × 5 × 4 = 19,200 핵심 호출).

## 문항 생성 원칙

- 의미 골격(slot)과 표현은 사람이 작성한 템플릿 (`src/gen/templates.py`). LLM은 의역 단계에서만, 사후 검토 대상.
- 자원/지출 금액은 base마다 다르게, 부족·충족 차이 크기(margin)를 기록해 난이도 분석에 쓴다.
- pilot base와 main base는 템플릿 조합·직업·지출 항목이 겹치지 않게 seed와 slot pool을 분리한다.
