# v0.1 설계 비판적 검토 (2026-10-05)

결론: **설계의 식별 논리는 좋지만, 지금 형태 그대로면 "효과 없음(ceiling)"으로 끝날 위험이 가장 크다.**
오늘 안에 pilot으로 go/no-go를 판정하고, 아래 수정 세 가지(R1–R3)를 반영하는 것을 권한다.

## 좋은 점 (유지)

- 참된 집단 차이 = 0을 설계로 보장 → "허위 집단 차이"가 깔끔한 estimand.
- 자원 변경쌍으로 "항상 같은 답" 모델의 허위 안정성 차단.
- 규범 판단에 정답을 강요하지 않음, 사실/규범 호출 분리, 기본 상황 단위 cluster bootstrap.
- 실패가 나올 때까지 문항을 바꾸지 않는다는 원칙.

## 주요 위험과 수정 제안

### R1. Ceiling / null 위험 (가장 큼)
"가용자원 600, 필수지출 1,000, 추가 자원 없음"은 사실상 산술 문제다. Qwen3-8B급도 정답률 ~100%,
활동 변경 flip ≈ 0일 가능성이 높다. 그러면 핵심 결과가 null이고 NAACL 본 학회 수준의 이야기가 약하다.

**수정:** 이진 사실 판정은 *조작 점검/이해 점검*으로 내리고, 주 종속변수에 **연속형 필요 측정**을 추가한다.
- 예: "On a 1–7 scale, how severe is this person's current material hardship?" / "How many dollars short are they?"
- 핵심: 이 척도에는 정답이 없어도 된다. **같은 물질적 사실에서 활동 정보만 바꿨을 때 값이 같아야 한다(불변성)**는 것이 정답이다.
- 이것이 사회과학에서 LLM을 "필요(need) 코딩 도구"로 쓰는 실제 사용 방식이고, 정치학적 측정 기여와 직결된다.
- 이진 판정에서 ceiling이 나와도, "사실은 맞게 읽는데 필요 *평가*는 노력 정보에 끌려간다"는 결과 자체가 논문이 된다.

### R2. FairFund-Bench와의 관계를 "경쟁"이 아니라 "대화"로
저장소를 직접 확인했다 (`data/external/fairfund-bench`, commit 74b75f3, 2026-09-16):
- 600 appeals × 5 names = 3,000 stimuli, 15 scenarios × 5 causal framings (no_cause, structural, self_cause, stigma_no_redemption, stigma_redemption).
- 과제는 Rate/Rank/Allocate "funding priority". 14개 API 모델 응답 107,940행 공개 (CC BY 4.0).
- **"deservingness alignment"는 프레이밍에 따라 배분이 달라지는 것을 *바람직한* 정렬로 점수화**한다.
- 같은 시나리오 안에서 프레이밍만 바뀌고 물질적 서술("used up the small amount I had saved up", "facing eviction")은 그대로다.

→ 우리의 질문은 그 바로 뒤에 있다: **프레이밍에 따른 배분 차이가 '정당성' 판단 때문인가, 아니면 '필요 측정' 자체가 오염되었기 때문인가?**
FairFund 자극문에 우리의 *need-only* 질문을 붙이면, 가장 가까운 선행연구 위에서 직접 외적 타당성 probe가 된다. 리뷰어 방어에 가장 강한 카드다.
(arXiv 2607.28934, 문헌 에이전트가 논문 본문 대조 중)

### R3. 정서가(valence) 대조가 빠지면 가장 큰 공격 포인트가 남는다
"1개만 지원" 문장은 그냥 부정적인 문장이다. 무관 정보 변경(신청 화면 표시)은 정서가가 중립이라 이 공격을 막지 못한다.
**수정:** "비도덕적 부정 정보" 대조 추가 — 정서적으로 부정적이지만 책임·노력과 무관한 사건
(예: "Their apartment building's elevator has been out of service for two weeks.").
이 조건에서 flip이 활동 조건보다 작아야 "도덕적 관련성" 효과라고 말할 수 있다.

### R4. 모델 구성: 리뷰어는 frontier 모델을 물어본다
오픈 ≤32B 네 개만 있으면 "작은 모델 문제 아닌가"라는 반론이 나온다.
API 예산이 있다면 frontier 1–2개를 핵심 960개(직접 질문 + 필요 척도)에만 돌리는 것을 권한다 (호출 수천 회, 저비용).

### R5. 일정
7일 안에 독립 검토자 2명의 문항 검토를 받으려면 **오늘 사람을 확보해야** 한다. 안 되면 limitation으로 명시하고 작성자 검토 + 사후 표본 검토로 간다.

### R6. 범위와 기대치
단일 도메인, 960 문항, 오픈 모델 4개 → 결과가 뚜렷하지 않으면 Findings 수준. R1–R2가 살아나면 long paper로 충분히 승부할 만하다.

## Go / no-go 기준 (10/6 오전까지 판정)

| pilot 결과 (Qwen3-8B, Ministral-3-8B) | 결정 |
| --- | --- |
| 이진 flip ≈ 0, 필요 척도 활동 효과도 ≈ 0, FairFund probe도 ≈ 0 | 강한 null → "LLM은 필요와 정당성을 분리한다" 경계조건 논문 또는 주제 재검토 |
| 이진 ceiling, 필요 척도/FairFund probe에서 활동·프레이밍 효과 有 | **주력 시나리오.** 척도 + 허위 집단 차이를 headline으로 |
| 이진 판정에서도 flip 有 | v0.1 그대로 진행 + R1–R3 보강 |
| 정의 제공 시 효과 소멸 | "질문 모호성" 결과로 범위를 좁혀 보고 (사전 등록한 해석) |
