# /solve — 수학 손글씨 풀이 생성기

수학 문제가 담긴 이미지·PDF에 손글씨 스타일 풀이를 오버레이한다.

## 사용법

```
/solve <filepath>
```

예시:
- `/solve ~/Downloads/homework.jpg`
- `/solve problem.pdf`
- `/solve /path/to/test.png`

## 지원 형식

JPG, JPEG, PNG, PDF

## 사전 조건

- `math-handwriting-solver` 설치 완료 (`pip install -e .` 또는 `pip install math-handwriting-solver`)
- `ANTHROPIC_API_KEY` 환경 변수 설정

## 실행 방법

1. filepath가 존재하는지 확인한다
2. 다음 명령을 실행한다:

```bash
python -m solver "<filepath>"
```

   `ANTHROPIC_API_KEY`가 환경 변수에 없으면 먼저 설정을 안내한다.

3. 출력 파일 경로를 사용자에게 알린다
4. confidence < 80%이면 "AI 풀이를 반드시 확인하세요" 경고를 함께 표시한다

## 출력 파일명

`{원본파일명}_solved.{확장자}` — 원본 파일은 수정되지 않는다.
