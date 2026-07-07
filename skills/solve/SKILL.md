---
name: solve
description: 수학 문제 이미지 또는 PDF를 입력받아 손글씨 스타일 풀이 overlay를 생성할 때 사용. 사용자가 시험지·문제지 사진으로 풀이를 요청하거나, /solve 를 호출할 때 트리거.
---

# /solve — Math Handwriting Solver

## Overview

수학 문제 이미지(JPG·PNG) 또는 PDF를 입력받아 Claude Vision으로 문제를 파악하고, 손글씨 스타일로 풀이를 원본 이미지 위에 오버레이해 출력합니다.

출력 형식은 인지과학 연구를 기반으로 설계됩니다:

| 원칙 | 설계 결정 | 출처 |
|------|-----------|------|
| Worked Example Effect | 모든 중간 단계 명시 | Barbieri et al. (2023) |
| Split-Attention Effect | 주석을 수식 바로 옆에 배치 | ZDM Springer (2022) |
| Strategic Color Coding | 역할별 5색 체계 | arXiv 2411.14605 |
| Concept Box Effect | 핵심 개념 박스 필수 | NWEA Mapping Math (2024) |

## When to Use

**Apply this skill when:**
- 사용자가 수학 문제 이미지 또는 PDF 파일 경로를 제공하며 풀이를 요청할 때
- `/solve` 명령을 명시적으로 호출할 때
- 시험지·교재·문제집 사진에서 손글씨 풀이 오버레이가 필요할 때
- 중등·고등 수학 범위(방정식, 함수, 기하, 통계 등)의 문제일 때

**When NOT to use:**
- 이미지나 PDF 파일이 없이 수식만 텍스트로 제공된 경우 (파일 없이 풀이만 요청 시에는 일반 대화로 처리)
- 수학이 아닌 과목(물리, 화학 등) — 현재 scope 밖
- 이미 풀린 풀이를 설명·검토만 원하는 경우
- 대학 수준 이상의 고급 수학 (proof, 추상대수 등)

## Loading Constraints

스킬 실행 전 반드시 순서대로 확인:

**1. 패키지 설치 확인**
```bash
python -m solver --help
```
실패 시: `pip install -e .` (repo 루트)

**2. API 키 확인**
```bash
echo $ANTHROPIC_API_KEY
```
비어 있으면: `export ANTHROPIC_API_KEY=<your-api-key>`

**3. 파일 존재 확인** — 경로가 유효한지 확인. 상대경로보다 절대경로 권장.

**4. 포맷 확인** — `jpg`, `jpeg`, `png`, `pdf` 만 지원.

## The Process

- [ ] **Step 1: 파일 확인**
  입력 파일 경로와 포맷 확인. 지원하지 않는 포맷이면 즉시 중단하고 지원 포맷 안내.

- [ ] **Step 2: 문제 파악**
  Claude Vision으로 이미지를 분석해 문제 유형·수식·요구사항 추출. 문제가 여러 개면 각 번호를 식별.

- [ ] **Step 3: 풀이 생성**
  추출된 문제를 단계별로 풀이. 각 단계는 학생이 따라갈 수 있도록 중간 계산을 생략하지 않음.

- [ ] **Step 4: overlay 렌더링**
  ```bash
  python -m solver "<filepath>"
  ```
  PIL + NanumPenScript 폰트로 손글씨 스타일 overlay 생성. 색상 체계는 아래 **Output** 참고.

- [ ] **Step 5: confidence 확인 및 사용자 안내**
  결과의 신뢰도를 확인하고 적절한 메시지 출력 (아래 confidence 표 참고).

- [ ] **Step 6: 학습 권장 메시지 추가**
  성공적으로 완료된 경우 반드시 다음 메시지를 출력:
  > "이 풀이를 한 번 읽은 후, 책을 덮고 혼자 다시 풀어보세요. 직접 풀어보는 것이 이해를 확인하는 가장 좋은 방법입니다."
  *(Worked Example Fading — Atkinson et al., 2000)*

## Output

**파일명:** `{stem}_solved{ext}` — 입력 파일과 같은 디렉터리에 저장

**Confidence 기준:**

| Confidence | 의미 | 사용자에게 전달 |
|------------|------|----------------|
| ≥ 0.85 | sympy 검증 통과 | 출력 경로만 안내, 경고 없음 |
| 0.80 – 0.85 | 경계 | "풀이를 확인해보는 것을 권장합니다" |
| < 0.80 | 낮은 신뢰도 | "AI 풀이를 반드시 확인하세요. 선생님께 검토를 받으세요" |

**Annotation 색상 체계:**

| 색상 | 역할 |
|------|------|
| blue | 풀이 단계, 수식 변환 |
| orange | 인수분해 힌트, 수치 보조 |
| green | 답 체크마크, 정답 강조 |
| red | 강조, 손그림 원 |
| purple | 핵심 개념 박스 (항상 마지막) |

## Example

**Without `/solve`:**
```
사용자: 이 문제 풀어줘 [이미지 첨부]
어시스턴트: x² + 9x - 22 = 0 에서 (x-2)(x+11)=0 이므로 x=2 또는 x=-11입니다.
```
→ 텍스트로만 답하고 이미지 overlay 없음. 학생이 어느 단계에서 틀렸는지 파악하기 어려움.

**With `/solve`:**
```
사용자: /solve /path/to/exam.jpg
어시스턴트:
[Prerequisites 체크 → 이미지 분석 → 단계별 풀이 → overlay 렌더링]
→ /path/to/exam_solved.jpg 저장 완료 (confidence: 0.92)
→ "이 풀이를 한 번 읽은 후, 책을 덮고 혼자 다시 풀어보세요."
```
→ 원본 시험지 위에 손글씨 스타일로 각 단계가 표시된 이미지 생성.

## Interaction with Other Skills

| 상황 | 연계 스킬 |
|------|-----------|
| PDF 여러 페이지 처리 | `batch-solve` (Stage 2 예정) |
| MCP 서버로 노출 | `mcp/` 디렉터리 참고 (Stage 2) |
| 풀이 결과 설명 요청 | 일반 대화로 처리, 이 스킬 불필요 |

## Common Rationalizations

스킬을 건너뛰려는 이유로 자주 등장하는 합리화:

- *"그냥 텍스트로 답해도 되지 않나?"* — overlay가 없으면 학생이 자신의 풀이 과정과 비교할 수 없음.
- *"이미지가 이미 있는데 prerequisites 확인이 필요한가?"* — API 키나 패키지 누락 시 런타임에 실패하므로 사전 확인 필요.
- *"confidence 경고는 귀찮다."* — 낮은 신뢰도를 무시하면 오답 풀이를 학생이 그대로 학습하는 위험이 있음.

## Red Flags

다음 상황이 보이면 즉시 멈추고 사용자에게 확인:

- 문제 이미지에서 수식이 인식되지 않거나 흐릿한 경우 — 더 선명한 이미지 요청
- Confidence < 0.80 — 풀이 결과를 그대로 전달하지 말고 검토 요청 안내
- 대학 수준(편미분, 선형대수, 복소해석 등) 문제 감지 — 스킬 scope 초과 명시
- 폰트 파일(`fonts/NanumPenScript-Regular.ttf`) 없음 — overlay 렌더링 불가, repo 재설치 안내
- 파일 경로에 한글이나 공백 포함 — 절대경로 + 따옴표 감싸기 필요

## Verification

스킬 완료 후 다음 항목을 확인:

- [ ] `{stem}_solved{ext}` 파일이 입력 파일과 같은 디렉터리에 생성됐는지
- [ ] overlay가 원본 이미지의 올바른 위치에 렌더링됐는지 (풀이 영역이 빈 공간에 배치)
- [ ] confidence 값이 출력됐고 해당 기준 메시지를 전달했는지
- [ ] 학습 권장 메시지("책을 덮고 혼자 다시 풀어보세요")가 포함됐는지
- [ ] 개념 박스(purple)가 풀이 마지막에 포함됐는지
