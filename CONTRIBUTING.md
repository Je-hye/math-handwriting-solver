# Contributing

이슈 제보와 PR을 환영합니다.

## 개발 환경 설정

```bash
git clone https://github.com/Je-hye/math-handwriting-solver.git
cd math-handwriting-solver
pip install -e ".[dev]"
```

테스트 실행:

```bash
pytest
```

## 이슈 제보

- 버그: 재현 방법, 입력 파일 종류, 오류 메시지를 포함해 주세요.
- 기능 요청: 사용 사례와 기대 동작을 설명해 주세요.

## Pull Request

1. `main`에서 브랜치를 만드세요 (`feat/...`, `fix/...`).
2. 핵심 로직 변경에는 테스트를 추가하세요.
3. `pytest` 전체 통과를 확인하세요.
4. PR 제목은 변경 내용을 명확하게 적어 주세요.

## 코드 스타일

- Python 3.11+ 타입 힌트 사용
- `from __future__ import annotations`
- 주석은 코드만으로 의도가 불명확할 때만 작성

## 라이선스

기여한 코드는 [MIT License](LICENSE) 조건으로 배포됩니다.
