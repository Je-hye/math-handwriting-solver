# Pre-Mortem: 수학 손글씨 풀이 생성기
_"6개월 후. 서비스는 살아 있다. 그런데 신뢰가 없다."_

## Executive Read

- **핵심 실패 서사:** 틀린 풀이가 완벽한 손글씨로 나가는 동안, API 비용과 운영 부하가 수익 없이 쌓인다
- **가장 큰 제품 리스크:** Silent Wrong Answer — 틀린 풀이가 완성된 것처럼 렌더링됨
- **가장 큰 신뢰 리스크:** Claude Vision 오독 → 완전히 다른 문제를 품
- **가장 큰 감정 손상 리스크:** 파일 손상 — "이 앱은 내 파일을 망친다"
- **가장 큰 운영 드래그 리스크:** 버스 팩터 1 + API 비용 무통제 폭발

## Moments of Truth — 가장 깨지기 쉬운 순간

- 첫 결과 확인 → 틀린 풀이가 자신감 있게 출력됨 → "이거 믿어도 되나?"
- 저화질 사진 제출 → Vision 오독 → 완전히 다른 문제 풀이 → 학생이 오답 공부
- 시험 기간 동시 접속 → rate limit 침묵 오류 → 흰 화면 → "갑자기 왜 안 됨?"
- PDF 처리 후 원본 덮어씀 → 나중에 파일 손상 발견 → 복구 불가

---

## 🔴 Critical Risks

### 1. Silent Wrong Answer (틀린 풀이가 완성된 것처럼 렌더링)

**What goes wrong:** 정확도 검증 레이어 없이 Claude 풀이가 바로 annotation으로 렌더링된다.  
**How users experience it:** 시각적으로 완벽한 손글씨 풀이 → 의심 없이 학습 → 시험에서 틀림 → 서비스 탓  
**Emotional impact:** 배신감 + 자책. 가장 회복 불가능한 신뢰 손상.  
**Chain of events:** 정확도 메트릭 없음 → LLM이 부호 오류·논리 비약으로 틀린 풀이 생성 → 손글씨 스타일로 예쁘게 출력 → 로그에는 성공(200 OK)  
**Why the team misses it:** "Claude는 수학 잘한다"는 막연한 신뢰. 정확도를 한 번도 측정하지 않음.  
**Likelihood:** High | **Impact:** Catastrophic | **Trust damage:** Very High | **Recoverability:** Hard  
**Confidence:** High — 어떤 LLM도 수학 100% 정확도는 불가능  
**Verify by:** 표준 중학교 수학 문제 50개 입력 → 정답률 수동 채점. 80% 미만이면 Phase 2 재고.  
**Sources:** Saboteur, Burned Expert, Customer Advocate, Pessimist (4개 역할 독립 수렴)  
**Mitigation:** sympy/WolframAlpha로 수치 검증 레이어 추가 + "AI 풀이는 참고용" 워터마크 + confidence 점수 표시 → By: 스킬 프로토타입 단계  
**Tripwire:** 첫 번째 "이 답이 틀린 것 같아요" 리포트

---

### 2. Claude Vision 오독 → 가스라이팅

**What goes wrong:** 저해상도·기울어진 사진에서 Vision이 수식 기호를 오독해 완전히 다른 문제를 푼다.  
**How users experience it:** 이상한 풀이를 받음 → "내가 문제를 잘못 이해한 건가?" → 자신을 의심  
**Emotional impact:** Gaslighting — 도구가 틀렸는지 자신이 틀렸는지 판단 불가.  
**Chain of events:** `x²` → `x2`로 오독, `÷` → `-`로 오독 → 다른 문제 풀이 생성 → 오류 로그 없음  
**Why the team misses it:** 개발 중 깔끔한 테스트 이미지만 사용. Vision API 정확도 통계 없음.  
**Likelihood:** High | **Impact:** Catastrophic | **Trust damage:** High | **Recoverability:** Hard  
**Confidence:** High  
**Verify by:** 스마트폰 촬영 이미지 100장(다양한 조명·각도)으로 Vision 파싱 정확도 수동 검수  
**Sources:** Saboteur, Customer Advocate  
**Mitigation:** Vision 결과를 사용자에게 먼저 보여주고 확인 받는 단계 추가 ("이 문제가 맞나요?") → By: MCP 단계  
**Tripwire:** 베타 테스터가 "풀이가 문제랑 다른 것 같다" 첫 보고

---

### 3. API 비용 무통제 폭발

**What goes wrong:** 캐싱 없는 Vision + Claude 이중 호출이 사용자 규모에 선형 이상으로 증가한다.  
**How users experience it:** 갑작스러운 사용 제한 또는 유료화 공지 → 배신감  
**Emotional impact:** "잘 쓰고 있었는데 갑자기 막혔다."  
**Chain of events:** 200명 × 시험 기간 동일 문제 반복 제출 → 월 $300~600 청구 → 수익화 없이 적자 → 서비스 품질 급락 또는 중단  
**Why the team misses it:** Phase 1에서 비용 무시할 수준. 대시보드·알림 없음.  
**Likelihood:** High | **Impact:** Catastrophic | **Trust damage:** High | **Recoverability:** Hard  
**Confidence:** High — 브리핑에 "캐싱 전략 없음" 명시됨  
**Verify by:** 100건 요청 시뮬레이션 → 월 예상 청구액 계산 → 손익분기점 역산  
**Sources:** Burned Expert, Pessimist  
**Mitigation:** 문제 텍스트 해시 기반 캐싱 + Anthropic 비용 알림 설정 + 사용자 쿼터 per user → By: MCP 단계 이전  
**Tripwire:** 월 청구액이 예상의 2배 초과하는 첫 번째 달

---

### 4. Nanum Pen Script 수식 기호 깨짐

**What goes wrong:** Nanum Pen Script에 수학 특수기호(∴, ∵, ≥, ≠, √ 등) 글리프가 없어서 □ 박스로 렌더링된다.  
**How users experience it:** 풀이에 □, ▯가 섞임 → 핵심 가치 제안 사라짐  
**Emotional impact:** 경멸 — "조잡하다. 이게 서비스냐."  
**Chain of events:** 중등 수학 특유의 논리기호·근호·부등호가 포함된 풀이 → Nanum 폰트에 글리프 없음 → PIL이 tofu 출력 → jitter까지 적용돼 흔들리는 □  
**Why the team misses it:** 테스트가 `x + 2 = 5` 수준 단순 방정식. 중등 특수기호 커버리지 확인 없음.  
**Likelihood:** Very High | **Impact:** Major | **Trust damage:** Medium | **Recoverability:** Easy  
**Confidence:** High — 로컬에서 √2, ∴, ≠ 하나만 렌더링하면 즉시 확인 가능  
**Verify by:** 중등 수학 전 단원 특수기호 목록 추출 → Nanum Pen Script 글리프 커버리지 확인  
**Sources:** Saboteur  
**Mitigation:** 수식 기호 전용 폴백 폰트 레이어 추가 (NanumGothic 또는 FreeMono) → By: 스킬 단계  
**Tripwire:** 첫 번째 근호/논리기호 포함 문제 렌더링 테스트

---

### 5. PDF 파일 손상

**What goes wrong:** PDF overlay 처리 중 DPI 손실·텍스트 레이어 제거·페이지 순서 변경이 발생한다.  
**How users experience it:** 원본 삭제 후 처리본 저장 → 나중에 파일 손상 발견 → 복구 불가  
**Emotional impact:** 공포 → "이 앱은 파일을 망친다" 서사 → 소셜 경고  
**Chain of events:** 스캔본·복합기 출력 PDF 제출 → PIL 처리 중 레이어 손실 → 병렬 처리 중 페이지 핸들 충돌 → 사용자가 원본 덮어씀 → 되돌릴 수 없음  
**Why the team misses it:** 표준 단일 페이지 PDF로만 테스트.  
**Likelihood:** Medium | **Impact:** Catastrophic | **Trust damage:** Very High | **Recoverability:** Hard  
**Confidence:** Medium  
**Verify by:** 10종 실제 학생 PDF (스캔본·복합기 출력 포함) 왕복 처리 테스트 + 원본 vs 출력 diff  
**Sources:** Saboteur, Historian, Customer Advocate  
**Mitigation:** 원본 파일 항상 별도 보존 + 출력은 새 파일로만 + "원본은 수정하지 않습니다" 명시 → By: 스킬 단계  
**Tripwire:** 첫 번째 "파일 이상해요" 리포트

---

## 🟠 Significant Risks

### 6. layout_annotations 좌표 오프셋 (DPI/해상도 불일치)

**What goes wrong:** PIL annotation 레이아웃이 72dpi 기준 픽셀 고정값으로 하드코딩되어, 150/300dpi 스캔본에서 풀이가 문제를 덮거나 여백 밖으로 나간다.  
**Confidence:** High | **Verify by:** 72/150/300dpi, A4/Letter 8종 조합으로 레이아웃 위치 검수  
**Mitigation:** DPI 감지 + 상대 좌표 시스템 사용 → By: 스킬 단계

### 7. 시험 기간 동시 요청 rate limit 침묵 오류

**What goes wrong:** 동기 처리 아키텍처가 동시 요청에서 Anthropic rate limit에 걸려 무음으로 실패한다.  
**Confidence:** High | **Verify by:** API rate limit 문서 확인 → 현재 구조 max concurrent 계산  
**Mitigation:** 비동기 큐 + graceful degradation + "사용량 많음" 메시지 → By: FastAPI 단계 이전

### 8. 버스 팩터 1 — 개발자 번아웃

**What goes wrong:** API 포맷 변경 하나가 파이프라인 전체를 조용히 망가뜨리는데, 수리할 사람이 1명이고 그 1명은 논문 마감 중이다.  
**Confidence:** High | **Verify by:** 파이프라인 6단계 각각에 "깨지면 몇 시간 내 감지 가능한가?" 자문  
**Mitigation:** 각 단계 자동 헬스체크 + 슬랙/이메일 알림 → By: MCP 단계

### 9. 배포 환경 폰트 불일치

**What goes wrong:** Nanum Pen Script가 로컬에만 설치되어 있어 Docker/Linux 서버에서 폰트 없이 배포된다.  
**Confidence:** High | **Verify by:** 클린 Docker 이미지에서 엔드투엔드 실행  
**Mitigation:** 폰트 번들링 + CI Docker 테스트 → By: MCP 단계 배포 직전

### 10. 무료 시작 → 유료 전환 충격

**What goes wrong:** 무료 기대 고착화 후 유료화 공지 → 리뷰 폭탄 + 이탈.  
**Confidence:** High | **Verify by:** Phase 2 이전에 가격 정책 초안 5명 반응 테스트  
**Mitigation:** 처음부터 "베타 무료, 이후 유료" 명시 → By: Phase 2 공개 전

---

## 🟡 Watch List

- **Jitter 효과 저해상도 판독 불가** — 72dpi 화면에서 글자 뭉개짐. 멀티 해상도 테스트로 조기 확인.
- **학생 학습 능력 퇴화** — 도구 의존으로 스스로 생각 안 함. 장기 교육적 해악. 교육 서비스 전환 시 페다고지 설계 필요.
- **손글씨 novelty 소진 → retention 0** — 7일 재방문율로 측정. 10명 1주 사용 인터뷰.
- **의존성 silent deprecation** — Pillow 메이저 업그레이드. dependabot + CI.

---

## Cross-Cutting Themes

1. **침묵 실패(Silent Failure)가 핵심 위협** — 비용 폭발·틀린 풀이·파일 손상·rate limit 오류 모두 에러 없이 발생. **Observability 부재**가 공통 원인.
2. **정확도가 UX보다 우선** — 교육 서비스에서 예쁜 손글씨보다 맞는 답이 먼저다.
3. **Phase 1 가정이 Phase 2에서 전부 깨진다** — 개인 도구 → 서비스 전환은 "사용자 더 받기"가 아니라 아키텍처 재설계다.

---

## 사용자의 감정 현실

- **기대:** "사진 찍어 올리면 선생님이 직접 푼 것처럼 나온다. 공부에 도움된다."
- **실패가 만든 감정:** 배신감(틀린 풀이), 가스라이팅(Vision 오독), 공포(파일 손상), 분노(시험 기간 먹통)
- **관계가 깨지는 순간:** 틀린 풀이를 믿고 시험에서 틀렸다는 걸 아는 순간
- **다른 사람에게 하는 말:** "기능은 신기한데 답이 틀릴 때 있어서 믿고 쓰기 어려워."

---

## The Uncomfortable Truth

캐싱 없고, 정확도 측정 없고, 수익 모델 없고, 운영 모니터링 없다 — 이 네 가지가 동시에 없는 서비스는 Phase 2 진입 자격이 없다. Phase 2 진입 조건을 지금 명시해야 한다.

---

## 권장 다음 단계

1. **지금 당장:** 중학교 수학 문제 50개로 Claude 정확도 측정 → 80% 미만이면 검증 레이어 필수
2. **스킬 단계 완료 조건 추가:**
   - [ ] Nanum Pen Script 글리프 커버리지 확인 + 폴백 폰트 구성
   - [ ] 다양한 해상도(72/150/300dpi) 렌더링 테스트
   - [ ] 원본 파일 보존 정책 구현
   - [ ] Vision 결과 사용자 확인 단계 (선택적)
3. **Phase 2 진입 조건 사전 정의:**
   - 정확도 기준선 확보 (목표 수치 결정 필요)
   - 비용 모델 + 사용자 쿼터 구현
   - 파이프라인 헬스체크 자동화
   - 수익화 정책 초안

---

_Generated: 2026-06-10 | Agents: Saboteur (subagent), Burned Expert + Historian (subagent), Customer Advocate + Pessimist + Emotional Witness (Gemini)_
