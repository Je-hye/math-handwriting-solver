# 수학 손글씨 풀이 생성기 — 설계 문서

_2026-06-10_

---

## 1. 핵심 가치 제안 (Steelmanned Thesis)

> 학생이 시험지에서 어떻게 풀어야 하는지 보여주는 손글씨 모델링

수학 문제 사진·PDF를 입력하면, 사람이 시험지에 직접 손으로 푼 것처럼 보이는 풀이를 원본 이미지 위에 오버레이해서 반환한다. 단순한 정답 제공이 아니라 **어떻게 풀어야 하는지** — 단계별 계산 과정, 강조 표시, 개념 메모까지 — 를 시각적으로 전달하는 것이 핵심 가치다.

손글씨 스타일이 강점의 출처다. 폰트 + jitter로 구현한 불완전한 필기체는 "AI가 만든 완벽한 텍스트"가 아니라 "선생님이 직접 써준 것 같은 느낌"을 만든다. 이것이 교육적 공감과 신뢰를 만드는 차별화 요소다.

---

## 2. 사용자

### 2.1 학생 (학습 목적)

- **목적:** 내가 어떻게 풀어야 하는지 이해
- **사용 맥락:** 모르는 문제 앞에서, 숙제 검토, 시험 준비
- **confidence 낮으면:** 출력 하단에 워터마크 표시 — "AI 풀이를 반드시 확인하세요"
- **UI 요구:** 간단한 파일 업로드, 빠른 결과

### 2.2 선생님 (자료 제작 목적)

- **목적:** 학생에게 나눠줄 손풀이 자료 생성
- **사용 맥락:** 수업 자료 준비, 오답 풀이 제공
- **워터마크 없음:** 선생님 모드 출력은 워터마크 미표시
- **수동 수정 가능:** annotation 위치·내용·색상을 출력 후 수동으로 편집할 수 있어야 함 (Phase 2 이후)

---

## 3. 입출력 스펙

| 항목 | 내용 |
|------|------|
| 입력 형식 | JPG, PNG, PDF |
| 출력 형식 | 입력과 동일한 형식 |
| 원본 보존 | **덮어쓰기 금지.** 원본은 항상 별도 보존, 출력은 새 파일로 |
| 수학 범위 | 중등 수학 (이후 확장) |
| 다중 페이지 | PDF 다중 페이지 지원 (Phase 1은 단일 페이지부터) |

**원본 보존 원칙:** `problem.jpg` 입력 시 `problem_solved.jpg` 생성. `problem.jpg`는 절대 수정하지 않는다.

---

## 4. 파이프라인

```
입력 파일
  │
  ▼
[1] parse_input          — 파일 형식 감지, DPI 정규화, 이미지 추출
  │
  ▼
[2] extract_problem      — Claude Vision API로 문제 텍스트·수식·그래프 영역 파악
  │  └─ 확인 단계: Vision 결과를 사용자에게 보여주고 "이 문제가 맞나요?" 확인
  ▼
[3] generate_solution    — Claude API로 단계별 풀이 생성
  │  └─ 수치 검증: sympy로 계산 결과 검증 → 불일치 시 confidence 하향
  ▼
[4] layout_annotations   — 풀이 단계를 annotation 목록으로 변환 + 위치 계산
  │  └─ 좌표는 72dpi 기준으로 정규화, 실제 DPI 변환은 이 단계에서
  ▼
[5] render_overlay       — PIL로 원본 이미지에 손글씨 annotation 렌더링
  │  └─ Nanum Pen Script + NanumGothic 폴백 + jitter 효과
  ▼
[6] save_output          — 원본 형식으로 저장 (새 파일)
  │
  ▼
출력 파일
```

**파이프라인 원칙:**
- 각 단계는 독립적으로 테스트 가능
- 단계 간 인터페이스는 데이터 모델(아래 5절) 기반
- 실패는 침묵하지 않는다 — 각 단계는 명시적 예외를 발생시킴

---

## 5. 데이터 모델

```python
@dataclass
class BoundingBox:
    x: float       # 72dpi 기준 정규화 좌표
    y: float
    width: float
    height: float

@dataclass
class Figure:
    type: Literal["graph", "geometry", "table"]
    bbox: BoundingBox

@dataclass
class Point:
    x: float       # 72dpi 기준 정규화 좌표
    y: float

@dataclass
class AnnotationStyle:
    rotation_deg: float      # ±3° 범위 jitter
    opacity: float           # 0.85~0.95
    font_size: int

@dataclass
class Annotation:
    type: Literal["circle", "arrow", "text", "underline", "checkmark", "box"]
    content: str
    position: Point
    color: Literal["blue", "red", "green", "orange", "purple"]
    style: AnnotationStyle

@dataclass
class ProblemData:
    text: str                # Vision OCR 결과
    problem_type: Literal["equation", "graph", "geometry", "statistics"]
    figures: list[Figure]    # 그래프·도형 영역
    bbox: BoundingBox        # 문제 영역 (annotation 배치 기준)
    raw_image: bytes         # 원본 이미지

@dataclass
class SolutionData:
    steps: list[str]
    final_answer: str
    annotations: list[Annotation]
    confidence: float        # 0.0~1.0; sympy 검증 실패 시 하향
    verified: bool           # sympy 검증 통과 여부
```

---

## 6. 색상 규칙

모든 annotation은 아래 색상 체계를 따른다.

| 색상 | 용도 | 예시 |
|------|------|------|
| 파란색 `blue` | 계산 과정, 수식 변환 | `y = (x-1)² - 4` |
| 빨간색 `red` | 강조, 동그라미 | 핵심 수식 동그라미, 경고 |
| 초록색 `green` | 정답 체크 | `✓`, 최종 답 표시 |
| 주황색 `orange` | 좌표·수치 라벨 | 꼭짓점 좌표, 교점 값 |
| **보라색 `purple`** | 풀이 하단 개념 설명 네모 박스 | "이차함수 표준형: y = a(x-p)² + q" |

**보라색 개념 박스:** 풀이 하단에 문제를 푸는 데 필요한 핵심 개념을 네모 박스 안에 보라색으로 작성한다. 학습 목적 사용자에게 "왜 이렇게 푸는지"를 알려주는 역할을 한다.

---

## 7. 렌더링

### Phase 1 — PIL + 폰트 + Jitter (현재 구현 목표)

**폰트 스택:**
1. Nanum Pen Script — 기본 손글씨 폰트 (한글 + 기본 수식)
2. NanumGothic 폴백 — 수학 특수기호(∴, ∵, ≥, ≠, √, ∫ 등) 커버

**Jitter 효과:**
- 무작위 회전: ±3°
- 위치 오프셋: 72dpi 기준 ±2px → 실제 DPI에 비례 스케일링
- 불투명도: 0.85~0.95

**DPI 정규화:**
- 모든 좌표·크기는 72dpi 기준으로 계산
- 실제 이미지 DPI 감지 후 `render_overlay` 단계에서 변환
- `offset_px = base_offset_72dpi × (actual_dpi / 72)`

### Phase 2 — SVG 경로 애니메이션 (별도 마일스톤)

- 글자·기호를 베지어 곡선 경로로 렌더링
- 필기 진행 애니메이션 (stroke-dashoffset)
- Phase 1 완료 + 품질 게이트 통과 후 착수

---

## 8. 개발 단계

### Stage 1: Claude Code 스킬 (프로토타입)

**목표:** 파이프라인 전체 검증, 핵심 품질 측정

```bash
/solve problem.jpg    # → problem_solved.jpg
/solve problem.pdf    # → problem_solved.pdf
```

**Stage 1 완료 조건 체크리스트:**
- [ ] Nanum Pen Script 글리프 커버리지 확인 + 폴백 폰트 구성
- [ ] 72 / 150 / 300dpi × A4 / Letter 8종 조합 렌더링 테스트
- [ ] Vision 정확도 측정: 중등 수학 50문제 → 80% 이상 통과
  - 80% 미만이면: "이 문제가 맞나요?" 확인 단계 Stage 1에서 추가
- [ ] Annotation 위치 정확도: 그래프 문제 10개 → annotation이 문제 bbox 바깥에 위치하면 통과
- [ ] PDF 왕복 테스트: 10종 (스캔본 포함) → 원본 보존 확인
- [ ] 원본 파일 보존 정책 구현 (덮어쓰기 없음)
- [ ] sympy 수치 검증 + confidence 낮으면 워터마크 출력

### Stage 2: MCP 서버 (개인 도구)

**목표:** Claude와 자연스럽게 연동, 운영 안정성 확보

**추가 항목:**
- [ ] 문제 텍스트 해시 기반 캐싱 (동일 문제 재요청 시 API 호출 없음)
- [ ] Anthropic API 비용 알림 설정 (월 $X 초과 시 경고)
- [ ] 사용자 쿼터 per user
- [ ] 파이프라인 헬스체크 자동화
- [ ] 폰트 Docker 번들링

### Stage 3: FastAPI 서비스 (웹 서비스)

**목표:** 학생·선생님 구분 UI, 수익화 준비

**추가 항목:**
- [ ] 비동기 큐 (시험 기간 동시 요청 처리)
- [ ] 학생 모드 / 선생님 모드 UI 분리
- [ ] 선생님 모드: annotation 수동 수정 인터페이스
- [ ] 수익화 정책 구현 ("베타 무료, 이후 유료" 명시)
- [ ] rate limit 명시적 오류 메시지 ("사용량이 많습니다. 잠시 후 다시 시도해주세요")

---

## 9. 품질 게이트

| 게이트 | 기준 | 측정 방법 | 실패 시 |
|--------|------|-----------|---------|
| Vision 정확도 | 80% 이상 | 중등 문제 50개 수동 채점 | Stage 1에서 사용자 확인 단계 추가 |
| Annotation 위치 | annotation bbox가 문제 bbox 바깥 | 그래프 문제 10개 검사 | layout_annotations 로직 수정 |
| 수치 검증 | sympy 통과 시 confidence ≥ 0.8 | sympy 자동 검증 | confidence 하향 + 워터마크 |
| 폰트 커버리지 | 중등 특수기호 전체 렌더링 | 기호 목록 렌더링 테스트 | 폴백 폰트 추가 |

**수치 검증 전략:**
1. sympy 우선 — 로컬, 무료, 빠름. 대수·미적분·수열 처리 가능.
2. WolframAlpha API 폴백 — sympy 처리 불가 영역 (복잡한 기하, 통계).
3. 둘 다 실패 → confidence 0.5 이하 → 학생 모드 워터마크 표시.

---

## 10. Pre-Mortem 대응표

| 리스크 | 대응 | 적용 단계 |
|--------|------|-----------|
| Silent Wrong Answer | sympy 검증 + confidence + 워터마크 | Stage 1 |
| Vision 오독 | "이 문제가 맞나요?" 확인 단계 | Stage 1 (Vision 80% 미만 시 필수) |
| API 비용 폭발 | 해시 캐싱 + 비용 알림 + 쿼터 | Stage 2 |
| 수식 기호 깨짐 | NanumGothic 폴백 폰트 | Stage 1 |
| PDF 파일 손상 | 원본 보존 정책 + 새 파일 출력 | Stage 1 |
| DPI 오프셋 | 72dpi 정규화 + DPI 스케일링 | Stage 1 |
| rate limit 침묵 | 비동기 큐 + 명시적 오류 | Stage 3 |
| 폰트 배포 불일치 | Docker 번들링 + CI 테스트 | Stage 2 |

전체 pre-mortem 리포트: `docs/pre-mortem/2026-06-10-math-solver-premortem.md`

---

## 11. 미결 항목

| # | 항목 | 결정 |
|---|------|------|
| 1 | Annotation 위치 허용 기준 | **B안 확정** — annotation bbox가 문제 bbox 바깥이면 통과 (픽셀 겹침 측정 불필요) |
| 2 | 선생님 모드 annotation 수동 수정 | **Stage 3 구현** — FastAPI UI에서 annotation 위치·내용·색상 편집 인터페이스 제공 |
| 3 | Vision 확인 단계 적용 시점 | **Stage 1부터 조건부 적용** — Vision 정확도 80% 미만이면 Stage 1에서 즉시 추가 |
| 4 | 개념 설명 박스 색상 | **보라색 확정** — 풀이 하단 네모 박스는 보라색 |
| 5 | WolframAlpha API 키 관리 | macOS Keychain 저장 필수, .env 파일 커밋 금지 |
| 6 | Phase 2 진입 조건 | Stage 1 완료 체크리스트 전체 통과 후 정의 |
