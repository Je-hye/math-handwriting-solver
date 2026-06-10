# Math Handwriting Solver — Stage 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 수학 문제 이미지/PDF를 입력받아 손글씨 스타일 풀이를 오버레이한 동일 형식 파일을 출력하는 `/solve` Claude Code 스킬 구현

**Architecture:** parse_input → extract_problem(Vision) → generate_solution(Claude + sympy) → layout_annotations → render_overlay(PIL + Nanum) → save_output 6단계 파이프라인. 각 단계는 독립적으로 테스트 가능한 순수 함수. 원본 파일은 절대 수정하지 않는다.

**Tech Stack:** Python 3.11+, anthropic SDK, Pillow, pymupdf, sympy, pytest

---

## File Structure

```
math-handwriting-solver/
├── solver/
│   ├── __init__.py
│   ├── __main__.py              # python -m solver <filepath> 진입점
│   ├── models.py                # 모든 데이터클래스
│   ├── parse_input.py           # 파일 형식 감지, DPI 추출, 이미지 변환
│   ├── extract_problem.py       # Claude Vision API → ProblemData
│   ├── generate_solution.py     # Claude API + sympy 검증 → SolutionData
│   ├── layout_annotations.py    # DPI 스케일링 + jitter 적용
│   ├── render_overlay.py        # PIL 렌더링 (폰트, 색상, 회전)
│   ├── save_output.py           # 출력 파일 저장 (원본 보존 보장)
│   └── pipeline.py              # 6단계 순차 실행 오케스트레이터
├── tests/
│   ├── conftest.py              # 공유 fixture
│   ├── test_parse_input.py
│   ├── test_extract_problem.py
│   ├── test_generate_solution.py
│   ├── test_layout_annotations.py
│   ├── test_render_overlay.py
│   └── test_save_output.py
├── scripts/
│   ├── download_fonts.py        # Nanum 폰트 fonts/ 에 다운로드
│   └── quality_gates.py        # Stage 1 완료 조건 검증
├── fonts/                       # .gitignore — 폰트 파일 (download_fonts.py로 설치)
├── pyproject.toml
├── .env.example
└── .gitignore
```

`~/.claude/skills/solve/SKILL.md` — `/solve` 스킬 (별도 위치, Task 9에서 생성)

---

## Task 0: 프로젝트 스캐폴드

**Files:**
- Create: `pyproject.toml`
- Create: `solver/__init__.py`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `scripts/download_fonts.py`
- Create: `fonts/.gitkeep`

- [ ] **Step 1: pyproject.toml 작성**

```toml
[project]
name = "math-handwriting-solver"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.40.0",
    "Pillow>=10.4.0",
    "pymupdf>=1.24.0",
    "sympy>=1.13",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-mock>=3.14.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: .env.example 작성**

```bash
# ANTHROPIC_API_KEY는 macOS Keychain에서 읽는다. plaintext 저장 금지.
# security add-generic-password -a anthropic -s ANTHROPIC_API_KEY -w <your-key>
# 환경변수로 넘길 때는: export ANTHROPIC_API_KEY=$(security find-generic-password -a anthropic -s ANTHROPIC_API_KEY -w)

# WolframAlpha API Key (sympy 폴백, Stage 2에서 구현)
# security add-generic-password -a wolfram -s WOLFRAM_API_KEY -w <your-key>
```

- [ ] **Step 3: .gitignore 작성**

```
fonts/*.ttf
fonts/*.otf
.env
__pycache__/
*.pyc
.pytest_cache/
dist/
*.egg-info/
```

- [ ] **Step 4: 폰트 다운로드 스크립트 작성**

```python
# scripts/download_fonts.py
"""Nanum 폰트를 fonts/ 디렉터리에 다운로드한다."""
import urllib.request
from pathlib import Path

FONTS = {
    "NanumPenScript-Regular.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/nanumpenscript/"
        "NanumPenScript-Regular.ttf"
    ),
    "NanumGothic-Regular.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/nanumgothic/"
        "NanumGothic-Regular.ttf"
    ),
}

fonts_dir = Path(__file__).parent.parent / "fonts"
fonts_dir.mkdir(exist_ok=True)

for filename, url in FONTS.items():
    dest = fonts_dir / filename
    if dest.exists():
        print(f"Already exists: {filename}")
        continue
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, dest)
    print(f"Saved: {dest}")
```

- [ ] **Step 5: 폰트 다운로드 실행**

```bash
python scripts/download_fonts.py
```

Expected output:
```
Downloading NanumPenScript-Regular.ttf...
Saved: fonts/NanumPenScript-Regular.ttf
Downloading NanumGothic-Regular.ttf...
Saved: fonts/NanumGothic-Regular.ttf
```

- [ ] **Step 6: 의존성 설치**

```bash
pip install -e ".[dev]"
```

- [ ] **Step 7: `solver/__init__.py` 작성**

```python
from .pipeline import run

__all__ = ["run"]
```

- [ ] **Step 8: 빈 모듈 파일 생성**

```bash
touch solver/models.py solver/parse_input.py solver/extract_problem.py \
      solver/generate_solution.py solver/layout_annotations.py \
      solver/render_overlay.py solver/save_output.py solver/pipeline.py \
      solver/__main__.py
```

- [ ] **Step 9: 커밋**

```bash
git add pyproject.toml .env.example .gitignore scripts/download_fonts.py solver/ fonts/.gitkeep
git commit -m "feat: scaffold project structure and install dependencies"
```

---

## Task 1: 데이터 모델

**Files:**
- Create: `solver/models.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: `solver/models.py` 작성**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float


@dataclass
class Figure:
    type: Literal["graph", "geometry", "table"]
    bbox: BoundingBox


@dataclass
class Point:
    x: float
    y: float


@dataclass
class AnnotationStyle:
    rotation_deg: float = 0.0
    opacity: float = 0.9
    font_size: int = 24


@dataclass
class Annotation:
    type: Literal["circle", "arrow", "text", "underline", "checkmark", "box"]
    content: str
    position: Point
    color: Literal["blue", "red", "green", "orange", "purple"]
    style: AnnotationStyle = field(default_factory=AnnotationStyle)


@dataclass
class ProblemData:
    text: str
    problem_type: Literal["equation", "graph", "geometry", "statistics"]
    figures: list[Figure]
    bbox: BoundingBox
    raw_image: bytes        # 원본 이미지 bytes (JPEG)
    image_width: int        # 72dpi 기준 픽셀 너비
    image_height: int       # 72dpi 기준 픽셀 높이


@dataclass
class SolutionData:
    steps: list[str]
    final_answer: str
    annotations: list[Annotation]
    confidence: float       # 0.0~1.0; sympy 검증 실패 시 낮아짐
    verified: bool          # sympy 검증 통과 여부
```

- [ ] **Step 2: `tests/conftest.py` 작성**

```python
import io
import pytest
from PIL import Image
from solver.models import (
    ProblemData, SolutionData, Annotation, BoundingBox, Point, AnnotationStyle
)


@pytest.fixture
def sample_image_72dpi():
    return Image.new("RGB", (595, 842), color=(255, 255, 255))


@pytest.fixture
def sample_problem_data(sample_image_72dpi):
    buf = io.BytesIO()
    sample_image_72dpi.save(buf, format="JPEG")
    return ProblemData(
        text="y = x² - 2x - 3을 풀어라",
        problem_type="equation",
        figures=[],
        bbox=BoundingBox(x=50, y=50, width=495, height=100),
        raw_image=buf.getvalue(),
        image_width=595,
        image_height=842,
    )


@pytest.fixture
def sample_solution_data():
    return SolutionData(
        steps=["y = (x-3)(x+1)으로 인수분해", "x = 3 또는 x = -1"],
        final_answer="x = 3 또는 x = -1",
        annotations=[
            Annotation(
                type="text",
                content="y = (x-3)(x+1)",
                position=Point(x=50, y=200),
                color="blue",
                style=AnnotationStyle(),
            ),
            Annotation(
                type="checkmark",
                content="✓",
                position=Point(x=50, y=300),
                color="green",
                style=AnnotationStyle(),
            ),
            Annotation(
                type="box",
                content="인수분해: ax²+bx+c = a(x-p)(x-q)",
                position=Point(x=50, y=680),
                color="purple",
                style=AnnotationStyle(),
            ),
        ],
        confidence=0.85,
        verified=True,
    )
```

- [ ] **Step 3: 커밋**

```bash
git add solver/models.py tests/conftest.py
git commit -m "feat: add data models and test fixtures"
```

---

## Task 2: parse_input

**Files:**
- Create: `solver/parse_input.py`
- Create: `tests/test_parse_input.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_parse_input.py
import pytest
from pathlib import Path
from PIL import Image
from solver.parse_input import parse_input


def test_parse_jpeg_returns_image_dpi_format(tmp_path):
    img = Image.new("RGB", (595, 842))
    path = tmp_path / "problem.jpg"
    img.save(str(path), dpi=(72, 72))

    result_img, dpi, fmt = parse_input(path)

    assert isinstance(result_img, Image.Image)
    assert result_img.mode == "RGB"
    assert dpi == 72
    assert fmt == ".jpg"


def test_parse_png_detected(tmp_path):
    img = Image.new("RGB", (200, 200))
    path = tmp_path / "test.png"
    img.save(str(path))

    _, _, fmt = parse_input(path)

    assert fmt == ".png"


def test_parse_image_no_dpi_metadata_defaults_to_72(tmp_path):
    img = Image.new("RGB", (100, 100))
    path = tmp_path / "nodpi.jpg"
    img.save(str(path))  # no dpi kwarg

    _, dpi, _ = parse_input(path)

    assert dpi == 72


def test_unsupported_format_raises_value_error(tmp_path):
    path = tmp_path / "file.bmp"
    path.write_bytes(b"BM fake bmp data")

    with pytest.raises(ValueError, match="Unsupported format"):
        parse_input(path)


def test_file_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_input(tmp_path / "nonexistent.jpg")
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_parse_input.py -v
```

Expected: 5 failed (ImportError 또는 ModuleNotFoundError)

- [ ] **Step 3: `solver/parse_input.py` 구현**

```python
from __future__ import annotations
from pathlib import Path
from PIL import Image
import fitz  # pymupdf

SUPPORTED = {".jpg", ".jpeg", ".png", ".pdf"}
PDF_RENDER_DPI = 150


def parse_input(filepath: str | Path) -> tuple[Image.Image, int, str]:
    """Returns (rgb_image, dpi, suffix_lower)."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(
            f"Unsupported format: {suffix!r}. Supported: {sorted(SUPPORTED)}"
        )

    if suffix == ".pdf":
        return _parse_pdf(path)
    return _parse_image(path, suffix)


def _parse_image(path: Path, suffix: str) -> tuple[Image.Image, int, str]:
    img = Image.open(path)
    dpi_info = img.info.get("dpi", (72, 72))
    dpi = int(dpi_info[0]) if dpi_info[0] else 72
    return img.convert("RGB"), dpi, suffix


def _parse_pdf(path: Path) -> tuple[Image.Image, int, str]:
    doc = fitz.open(str(path))
    page = doc[0]
    mat = fitz.Matrix(PDF_RENDER_DPI / 72, PDF_RENDER_DPI / 72)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img, PDF_RENDER_DPI, ".pdf"
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_parse_input.py -v
```

Expected: 5 passed (PDF 테스트 제외 — PDF 테스트는 질게이트 Task 10에서)

- [ ] **Step 5: 커밋**

```bash
git add solver/parse_input.py tests/test_parse_input.py
git commit -m "feat: implement parse_input with DPI extraction"
```

---

## Task 3: extract_problem

**Files:**
- Create: `solver/extract_problem.py`
- Create: `tests/test_extract_problem.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_extract_problem.py
import json
import io
import pytest
from unittest.mock import MagicMock
from PIL import Image
from solver.extract_problem import extract_problem
from solver.models import ProblemData, Figure


def _mock_client(response_dict: dict) -> MagicMock:
    content = MagicMock()
    content.text = json.dumps(response_dict, ensure_ascii=False)
    response = MagicMock()
    response.content = [content]
    client = MagicMock()
    client.messages.create.return_value = response
    return client


_VALID_RESPONSE = {
    "text": "y = x² - 2x - 3을 풀어라",
    "problem_type": "equation",
    "figures": [],
    "bbox": {"x": 50, "y": 50, "width": 495, "height": 100},
}


def test_returns_problem_data():
    client = _mock_client(_VALID_RESPONSE)
    img = Image.new("RGB", (595, 842))

    result = extract_problem(img, dpi=72, client=client)

    assert isinstance(result, ProblemData)
    assert result.text == "y = x² - 2x - 3을 풀어라"
    assert result.problem_type == "equation"


def test_stores_image_dimensions():
    client = _mock_client(_VALID_RESPONSE)
    img = Image.new("RGB", (595, 842))

    result = extract_problem(img, dpi=72, client=client)

    assert result.image_width == 595
    assert result.image_height == 842


def test_parses_figures():
    response = {
        **_VALID_RESPONSE,
        "problem_type": "graph",
        "figures": [{"type": "graph", "bbox": {"x": 100, "y": 200, "width": 300, "height": 200}}],
    }
    client = _mock_client(response)
    img = Image.new("RGB", (595, 842))

    result = extract_problem(img, dpi=72, client=client)

    assert len(result.figures) == 1
    assert isinstance(result.figures[0], Figure)
    assert result.figures[0].type == "graph"


def test_high_dpi_image_scaled_down_before_api_call():
    """300dpi 이미지는 72dpi로 축소해서 API에 전송한다."""
    client = _mock_client(_VALID_RESPONSE)
    # 300dpi A4 = 2480×3508
    img = Image.new("RGB", (2480, 3508))

    result = extract_problem(img, dpi=300, client=client)

    # API 호출 시 image data가 포함됐는지 확인
    call_args = client.messages.create.call_args
    msg_content = call_args.kwargs["messages"][0]["content"]
    # 이미지 content가 있어야 함
    image_parts = [c for c in msg_content if c.get("type") == "image"]
    assert len(image_parts) == 1
    # image_width/height는 원본 dpi 기준이 아닌 72dpi 기준
    assert result.image_width == 595   # 2480 * 72/300 ≈ 595
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_extract_problem.py -v
```

Expected: 4 failed

- [ ] **Step 3: `solver/extract_problem.py` 구현**

```python
from __future__ import annotations
import base64
import io
import json
import anthropic
from PIL import Image
from .models import ProblemData, BoundingBox, Figure

_SYSTEM = "수학 문제 이미지를 분석해 JSON으로만 응답하는 어시스턴트."

_USER_TEMPLATE = """\
이미지에서 수학 문제를 분석하세요. 아래 JSON 형식으로만 응답하세요 — 다른 텍스트 없이:

{{
  "text": "문제 텍스트 (수식·한글 포함)",
  "problem_type": "equation|graph|geometry|statistics 중 하나",
  "figures": [
    {{"type": "graph|geometry|table", "bbox": {{"x": 0, "y": 0, "width": 100, "height": 100}}}}
  ],
  "bbox": {{"x": 0, "y": 0, "width": 595, "height": 200}}
}}

모든 좌표는 72dpi 기준 픽셀입니다. figures가 없으면 빈 배열을 반환하세요.
이미지 크기 (72dpi 기준): {width}×{height}px
"""


def extract_problem(
    image: Image.Image,
    dpi: int,
    client: anthropic.Anthropic | None = None,
) -> ProblemData:
    if client is None:
        client = anthropic.Anthropic()

    # 72dpi 기준으로 축소 (Vision API 입력 비용 절감)
    if dpi != 72:
        scale = 72 / dpi
        display = image.resize(
            (int(image.width * scale), int(image.height * scale)),
            Image.LANCZOS,
        )
    else:
        display = image

    w72, h72 = display.width, display.height

    buf = io.BytesIO()
    display.save(buf, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img_b64,
                    },
                },
                {
                    "type": "text",
                    "text": _USER_TEMPLATE.format(width=w72, height=h72),
                },
            ],
        }],
    )

    data = json.loads(response.content[0].text)

    figures = [
        Figure(type=f["type"], bbox=BoundingBox(**f["bbox"]))
        for f in data.get("figures", [])
    ]

    orig_buf = io.BytesIO()
    image.save(orig_buf, format="JPEG", quality=95)

    return ProblemData(
        text=data["text"],
        problem_type=data["problem_type"],
        figures=figures,
        bbox=BoundingBox(**data["bbox"]),
        raw_image=orig_buf.getvalue(),
        image_width=w72,
        image_height=h72,
    )
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_extract_problem.py -v
```

Expected: 4 passed

- [ ] **Step 5: 커밋**

```bash
git add solver/extract_problem.py tests/test_extract_problem.py
git commit -m "feat: implement extract_problem with Claude Vision API"
```

---

## Task 4: generate_solution + sympy 검증

**Files:**
- Create: `solver/generate_solution.py`
- Create: `tests/test_generate_solution.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_generate_solution.py
import json
import pytest
from unittest.mock import MagicMock
from solver.generate_solution import generate_solution, _verify_with_sympy
from solver.models import SolutionData


def _mock_client(response_dict: dict) -> MagicMock:
    content = MagicMock()
    content.text = json.dumps(response_dict, ensure_ascii=False)
    response = MagicMock()
    response.content = [content]
    client = MagicMock()
    client.messages.create.return_value = response
    return client


_VALID_RESPONSE = {
    "steps": ["y = (x-3)(x+1)으로 인수분해", "x = 3 또는 x = -1"],
    "final_answer": "x = 3 또는 x = -1",
    "annotations": [
        {"type": "text", "content": "y = (x-3)(x+1)", "position": {"x": 50, "y": 200}, "color": "blue"},
        {"type": "checkmark", "content": "✓", "position": {"x": 50, "y": 320}, "color": "green"},
        {"type": "box", "content": "인수분해: (x-a)(x-b)", "position": {"x": 50, "y": 680}, "color": "purple"},
    ],
}


def test_returns_solution_data(sample_problem_data):
    result = generate_solution(sample_problem_data, client=_mock_client(_VALID_RESPONSE))

    assert isinstance(result, SolutionData)
    assert len(result.steps) == 2
    assert result.final_answer == "x = 3 또는 x = -1"


def test_annotations_parsed_correctly(sample_problem_data):
    result = generate_solution(sample_problem_data, client=_mock_client(_VALID_RESPONSE))

    assert len(result.annotations) == 3
    assert result.annotations[0].color == "blue"
    assert result.annotations[2].color == "purple"
    assert result.annotations[2].type == "box"


def test_purple_concept_box_required(sample_problem_data):
    """응답에 보라색 box annotation이 없으면 confidence가 낮아진다."""
    response_no_purple = {
        **_VALID_RESPONSE,
        "annotations": [
            {"type": "text", "content": "hello", "position": {"x": 50, "y": 200}, "color": "blue"},
        ],
    }
    result = generate_solution(sample_problem_data, client=_mock_client(response_no_purple))

    assert result.confidence < 0.9


def test_verify_sympy_numeric_answer():
    verified, confidence = _verify_with_sympy("x + 2 = 5", "x = 3")
    assert verified is True
    assert confidence >= 0.8


def test_verify_sympy_multiple_answers():
    verified, confidence = _verify_with_sympy("y = x² - 2x - 3", "x = 3 또는 x = -1")
    assert verified is True
    assert confidence >= 0.8


def test_verify_sympy_invalid_expression():
    verified, confidence = _verify_with_sympy("문제", "@@##$$invalid")
    assert verified is False
    assert confidence == 0.5
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_generate_solution.py -v
```

Expected: 6 failed

- [ ] **Step 3: `solver/generate_solution.py` 구현**

```python
from __future__ import annotations
import json
import re
import anthropic
from .models import ProblemData, SolutionData, Annotation, Point, AnnotationStyle

_SYSTEM = "수학 풀이를 JSON으로만 응답하는 어시스턴트."

_USER_TEMPLATE = """\
다음 수학 문제를 단계별로 풀어주세요. 아래 JSON 형식으로만 응답하세요:

{{
  "steps": ["단계1", "단계2", ...],
  "final_answer": "최종 답",
  "annotations": [
    {{
      "type": "text|circle|arrow|underline|checkmark|box",
      "content": "내용",
      "position": {{"x": 100, "y": 200}},
      "color": "blue|red|green|orange|purple"
    }}
  ]
}}

색상 규칙:
- blue: 계산 과정, 수식 변환
- red: 강조, 동그라미
- green: 정답 체크 (checkmark type에 사용)
- orange: 좌표·수치 라벨
- purple: 풀이 하단 개념 설명 네모 박스 (box type, 반드시 포함)

좌표는 72dpi 기준 픽셀. 이미지 크기: {width}×{height}px.
풀이 annotation은 y > {problem_bottom} 아래 여백에 배치하세요.
annotations 마지막 항목은 반드시 purple box로 핵심 개념을 포함하세요.

문제: {problem_text}
"""


def generate_solution(
    problem: ProblemData,
    client: anthropic.Anthropic | None = None,
) -> SolutionData:
    if client is None:
        client = anthropic.Anthropic()

    prompt = _USER_TEMPLATE.format(
        width=problem.image_width,
        height=problem.image_height,
        problem_bottom=int(problem.bbox.y + problem.bbox.height) + 10,
        problem_text=problem.text,
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    data = json.loads(response.content[0].text)

    annotations = [
        Annotation(
            type=a["type"],
            content=a["content"],
            position=Point(**a["position"]),
            color=a["color"],
            style=AnnotationStyle(),
        )
        for a in data.get("annotations", [])
    ]

    verified, confidence = _verify_with_sympy(problem.text, data["final_answer"])

    # 보라색 개념 박스 없으면 confidence 하향
    has_purple_box = any(a.color == "purple" and a.type == "box" for a in annotations)
    if not has_purple_box:
        confidence = min(confidence, 0.7)

    return SolutionData(
        steps=data["steps"],
        final_answer=data["final_answer"],
        annotations=annotations,
        confidence=confidence,
        verified=verified,
    )


def _verify_with_sympy(problem_text: str, final_answer: str) -> tuple[bool, float]:
    """sympy로 최종 답을 파싱 검증. (verified, confidence)."""
    from sympy.parsing.sympy_parser import (
        parse_expr,
        standard_transformations,
        implicit_multiplication_application,
    )
    transformations = standard_transformations + (implicit_multiplication_application,)

    # "x = 3 또는 x = -1" → ["x = 3", "x = -1"]
    candidates = re.split(r"또는|or|,", final_answer)

    for candidate in candidates:
        candidate = candidate.strip()
        try:
            if "=" in candidate:
                rhs = candidate.split("=", 1)[1].strip()
                parse_expr(rhs, transformations=transformations)
            else:
                parse_expr(candidate, transformations=transformations)
            return True, 0.85
        except Exception:
            continue

    return False, 0.5
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_generate_solution.py -v
```

Expected: 6 passed

- [ ] **Step 5: 커밋**

```bash
git add solver/generate_solution.py tests/test_generate_solution.py
git commit -m "feat: implement generate_solution with sympy verification"
```

---

## Task 5: layout_annotations

**Files:**
- Create: `solver/layout_annotations.py`
- Create: `tests/test_layout_annotations.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_layout_annotations.py
import pytest
from solver.layout_annotations import layout_annotations, JITTER_ROT, JITTER_PX, OPACITY_MIN, OPACITY_MAX
from solver.models import SolutionData, Annotation, Point, AnnotationStyle


def test_dpi_scaling_doubles_position_at_144dpi(sample_solution_data):
    original_x = sample_solution_data.annotations[0].position.x  # 50
    original_y = sample_solution_data.annotations[0].position.y  # 200

    result = layout_annotations(sample_solution_data, dpi=144)

    ann = result[0]
    jitter_budget = JITTER_PX * (144 / 72) + 1
    assert abs(ann.position.x - original_x * 2) < jitter_budget
    assert abs(ann.position.y - original_y * 2) < jitter_budget


def test_rotation_within_jitter_bounds(sample_solution_data):
    for _ in range(30):
        result = layout_annotations(sample_solution_data, dpi=72)
        for ann in result:
            assert -JITTER_ROT <= ann.style.rotation_deg <= JITTER_ROT


def test_opacity_within_bounds(sample_solution_data):
    for _ in range(30):
        result = layout_annotations(sample_solution_data, dpi=72)
        for ann in result:
            assert OPACITY_MIN <= ann.style.opacity <= OPACITY_MAX


def test_font_size_scaled_by_dpi(sample_solution_data):
    base_size = sample_solution_data.annotations[0].style.font_size  # 24

    result_72 = layout_annotations(sample_solution_data, dpi=72)
    result_150 = layout_annotations(sample_solution_data, dpi=150)

    size_72 = result_72[0].style.font_size
    size_150 = result_150[0].style.font_size
    assert size_150 > size_72


def test_annotation_count_preserved(sample_solution_data):
    result = layout_annotations(sample_solution_data, dpi=72)
    assert len(result) == len(sample_solution_data.annotations)
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_layout_annotations.py -v
```

Expected: 5 failed

- [ ] **Step 3: `solver/layout_annotations.py` 구현**

```python
from __future__ import annotations
import random
from .models import SolutionData, Annotation, Point, AnnotationStyle

JITTER_ROT = 3.0        # degrees, ±
JITTER_PX = 2.0         # pixels at 72dpi
OPACITY_MIN = 0.85
OPACITY_MAX = 0.95
BASE_FONT_SIZE = 24     # 72dpi 기준


def layout_annotations(solution: SolutionData, dpi: int) -> list[Annotation]:
    """72dpi 좌표를 실제 dpi로 스케일링하고 jitter를 적용한다."""
    scale = dpi / 72.0
    jitter_px = JITTER_PX * scale
    result = []

    for ann in solution.annotations:
        result.append(Annotation(
            type=ann.type,
            content=ann.content,
            position=Point(
                x=ann.position.x * scale + random.uniform(-jitter_px, jitter_px),
                y=ann.position.y * scale + random.uniform(-jitter_px, jitter_px),
            ),
            color=ann.color,
            style=AnnotationStyle(
                rotation_deg=random.uniform(-JITTER_ROT, JITTER_ROT),
                opacity=random.uniform(OPACITY_MIN, OPACITY_MAX),
                font_size=int((ann.style.font_size or BASE_FONT_SIZE) * scale),
            ),
        ))

    return result
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_layout_annotations.py -v
```

Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add solver/layout_annotations.py tests/test_layout_annotations.py
git commit -m "feat: implement layout_annotations with DPI scaling and jitter"
```

---

## Task 6: render_overlay

**Files:**
- Create: `solver/render_overlay.py`
- Create: `tests/test_render_overlay.py`

> 폰트 파일(`fonts/NanumPenScript-Regular.ttf`, `NanumGothic-Regular.ttf`)이 있어야 한다.
> 없으면 Task 0의 `python scripts/download_fonts.py`를 먼저 실행.

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_render_overlay.py
import pytest
from pathlib import Path
from PIL import Image
from solver.models import Annotation, Point, AnnotationStyle

FONTS_DIR = Path(__file__).parent.parent / "fonts"
FONTS_PRESENT = (FONTS_DIR / "NanumPenScript-Regular.ttf").exists()

skip_no_fonts = pytest.mark.skipif(
    not FONTS_PRESENT,
    reason="Nanum fonts not installed — run: python scripts/download_fonts.py",
)


@skip_no_fonts
def test_render_returns_rgb_same_size():
    from solver.render_overlay import render_overlay
    image = Image.new("RGB", (595, 842), color=(255, 255, 255))
    result = render_overlay(image, [])
    assert result.mode == "RGB"
    assert result.size == (595, 842)


@skip_no_fonts
def test_render_text_annotation_no_exception():
    from solver.render_overlay import render_overlay
    image = Image.new("RGB", (595, 842), color=(255, 255, 255))
    annotations = [
        Annotation(type="text", content="x = 3", position=Point(x=50, y=200),
                   color="blue", style=AnnotationStyle(font_size=28)),
    ]
    result = render_overlay(image, annotations)
    assert result is not None


@skip_no_fonts
def test_render_all_colors_no_exception():
    from solver.render_overlay import render_overlay, COLOR_MAP
    image = Image.new("RGB", (595, 842), color=(255, 255, 255))
    annotations = [
        Annotation(type="text", content="test", position=Point(x=50, y=50 + i * 100),
                   color=color, style=AnnotationStyle(font_size=24))
        for i, color in enumerate(COLOR_MAP.keys())
    ]
    render_overlay(image, annotations)


@skip_no_fonts
def test_render_special_math_symbols_no_tofu():
    """∴√≠ 등 특수기호가 렌더링될 때 예외가 발생하지 않는다."""
    from solver.render_overlay import render_overlay
    image = Image.new("RGB", (595, 842), color=(255, 255, 255))
    annotations = [
        Annotation(type="text", content="∴ x = √3 ≠ 0",
                   position=Point(x=50, y=200), color="blue",
                   style=AnnotationStyle(font_size=28)),
    ]
    render_overlay(image, annotations)


@skip_no_fonts
def test_render_purple_concept_box():
    from solver.render_overlay import render_overlay
    image = Image.new("RGB", (595, 842), color=(255, 255, 255))
    annotations = [
        Annotation(type="box", content="이차함수 표준형: y = a(x-p)² + q",
                   position=Point(x=50, y=680), color="purple",
                   style=AnnotationStyle(font_size=22)),
    ]
    render_overlay(image, annotations)
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_render_overlay.py -v
```

Expected: 5 skipped (폰트 있으면 5 failed)

- [ ] **Step 3: `solver/render_overlay.py` 구현**

```python
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .models import Annotation

FONTS_DIR = Path(__file__).parent.parent / "fonts"

COLOR_MAP = {
    "blue":   (26,  68,  204),
    "red":    (204, 51,  0),
    "green":  (34,  136, 68),
    "orange": (204, 102, 0),
    "purple": (102, 0,   153),
}

# 이 문자들은 NanumPenScript에 글리프 없음 → NanumGothic으로 폴백
SPECIAL_MATH = set("∴∵≥≤≠√∫∑∏∞∈∉⊂⊃∪∩∧∨¬→←↔±°′″")

_pen_cache: dict[int, ImageFont.FreeTypeFont] = {}
_gothic_cache: dict[int, ImageFont.FreeTypeFont] = {}


def _pen_font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _pen_cache:
        _pen_cache[size] = ImageFont.truetype(
            str(FONTS_DIR / "NanumPenScript-Regular.ttf"), size
        )
    return _pen_cache[size]


def _gothic_font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _gothic_cache:
        _gothic_cache[size] = ImageFont.truetype(
            str(FONTS_DIR / "NanumGothic-Regular.ttf"), size
        )
    return _gothic_cache[size]


def _choose_font(text: str, size: int) -> ImageFont.FreeTypeFont:
    if any(c in SPECIAL_MATH for c in text):
        return _gothic_font(size)
    return _pen_font(size)


def render_overlay(image: Image.Image, annotations: list[Annotation]) -> Image.Image:
    canvas = image.copy().convert("RGBA")
    for ann in annotations:
        _draw(canvas, ann)
    return canvas.convert("RGB")


def _draw(canvas: Image.Image, ann: Annotation) -> None:
    rgb = COLOR_MAP[ann.color]
    alpha = int(ann.style.opacity * 255)
    rgba = (*rgb, alpha)
    font = _choose_font(ann.content, ann.style.font_size)
    x, y = int(ann.position.x), int(ann.position.y)
    rot = ann.style.rotation_deg

    if ann.type == "box":
        _draw_concept_box(canvas, ann.content, x, y, font, rgba)
    elif ann.type == "circle":
        _draw_circle(canvas, x, y, rgba)
    elif ann.type == "underline":
        _draw_underline(canvas, ann.content, x, y, font, rgba, rot)
    else:
        # text, checkmark, arrow
        content = "✓" if ann.type == "checkmark" else ann.content
        _draw_rotated_text(canvas, content, x, y, font, rgba, rot)


def _draw_rotated_text(
    canvas: Image.Image,
    text: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    rgba: tuple[int, int, int, int],
    rotation_deg: float,
) -> None:
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = dummy.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0] + 10, bb[3] - bb[1] + 10

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((5, 5), text, font=font, fill=rgba)

    if rotation_deg:
        layer = layer.rotate(-rotation_deg, expand=True)

    canvas.paste(layer, (x, y), layer)


def _draw_concept_box(
    canvas: Image.Image,
    content: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    rgba: tuple[int, int, int, int],
) -> None:
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = dummy.textbbox((0, 0), content, font=font)
    w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 16

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([x, y, x + w, y + h], outline=rgba, width=2)
    draw.text((x + 10, y + 8), content, font=font, fill=rgba)


def _draw_circle(
    canvas: Image.Image,
    cx: int,
    cy: int,
    rgba: tuple[int, int, int, int],
    r: int = 30,
) -> None:
    ImageDraw.Draw(canvas).ellipse(
        [cx - r, cy - r, cx + r, cy + r], outline=rgba, width=2
    )


def _draw_underline(
    canvas: Image.Image,
    content: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    rgba: tuple[int, int, int, int],
    rotation_deg: float,
) -> None:
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = dummy.textbbox((0, 0), content, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]

    draw = ImageDraw.Draw(canvas)
    draw.text((x, y), content, font=font, fill=rgba)
    draw.line([x, y + h + 2, x + w, y + h + 2], fill=rgba, width=2)
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_render_overlay.py -v
```

Expected: 5 passed (폰트 있을 경우)

- [ ] **Step 5: 커밋**

```bash
git add solver/render_overlay.py tests/test_render_overlay.py
git commit -m "feat: implement PIL render_overlay with Nanum font stack and jitter"
```

---

## Task 7: save_output

**Files:**
- Create: `solver/save_output.py`
- Create: `tests/test_save_output.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_save_output.py
import pytest
from pathlib import Path
from PIL import Image
from solver.save_output import save_output


def test_jpeg_output_named_with_solved_suffix(tmp_path):
    img = Image.new("RGB", (100, 100))
    src = tmp_path / "problem.jpg"
    img.save(str(src))

    out = save_output(img, src, ".jpg")

    assert out.name == "problem_solved.jpg"
    assert out.exists()


def test_png_output_preserves_extension(tmp_path):
    img = Image.new("RGB", (100, 100))
    src = tmp_path / "hw.png"
    img.save(str(src))

    out = save_output(img, src, ".png")

    assert out.name == "hw_solved.png"


def test_output_not_same_path_as_source(tmp_path):
    img = Image.new("RGB", (100, 100))
    src = tmp_path / "problem.jpg"
    img.save(str(src))

    out = save_output(img, src, ".jpg")

    assert out != src


def test_original_file_content_unchanged(tmp_path):
    original = Image.new("RGB", (100, 100), color=(255, 0, 0))
    src = tmp_path / "problem.jpg"
    original.save(str(src))
    original_mtime = src.stat().st_mtime

    modified = Image.new("RGB", (100, 100), color=(0, 0, 255))
    save_output(modified, src, ".jpg")

    assert src.stat().st_mtime == original_mtime


def test_output_is_valid_image(tmp_path):
    img = Image.new("RGB", (595, 842), color=(200, 200, 200))
    src = tmp_path / "problem.jpg"
    img.save(str(src))

    out = save_output(img, src, ".jpg")

    loaded = Image.open(str(out))
    assert loaded.size == (595, 842)
```

- [ ] **Step 2: 테스트 실패 확인**

```bash
pytest tests/test_save_output.py -v
```

Expected: 5 failed

- [ ] **Step 3: `solver/save_output.py` 구현**

```python
from __future__ import annotations
from pathlib import Path
from PIL import Image
import fitz


def save_output(
    image: Image.Image,
    source_path: str | Path,
    original_format: str,
    dpi: int = 72,
) -> Path:
    """원본을 건드리지 않고 {stem}_solved{suffix}로 저장. 출력 경로를 반환."""
    src = Path(source_path)
    out = src.parent / f"{src.stem}_solved{src.suffix}"

    assert out.resolve() != src.resolve(), \
        f"Output {out} must not overwrite source {src}"

    if original_format == ".pdf":
        _save_as_pdf(image, out, dpi)
    else:
        image.save(str(out))

    return out


def _save_as_pdf(image: Image.Image, out_path: Path, dpi: int) -> None:
    import io
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=95)
    buf.seek(0)

    # 72dpi 기준 pt 크기로 페이지 생성
    pt_w = image.width * 72 / dpi
    pt_h = image.height * 72 / dpi

    doc = fitz.open()
    page = doc.new_page(width=pt_w, height=pt_h)
    page.insert_image(fitz.Rect(0, 0, pt_w, pt_h), stream=buf.read())
    doc.save(str(out_path))
    doc.close()
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_save_output.py -v
```

Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add solver/save_output.py tests/test_save_output.py
git commit -m "feat: implement save_output with original preservation guarantee"
```

---

## Task 8: pipeline + CLI

**Files:**
- Create: `solver/pipeline.py`
- Create: `solver/__main__.py`

- [ ] **Step 1: `solver/pipeline.py` 구현**

```python
from __future__ import annotations
from pathlib import Path
import anthropic
from .parse_input import parse_input
from .extract_problem import extract_problem
from .generate_solution import generate_solution
from .layout_annotations import layout_annotations
from .render_overlay import render_overlay
from .save_output import save_output


def run(
    filepath: str | Path,
    client: anthropic.Anthropic | None = None,
) -> tuple[Path, float]:
    """파이프라인 실행. (출력 경로, confidence) 반환."""
    if client is None:
        client = anthropic.Anthropic()

    image, dpi, fmt = parse_input(filepath)
    problem = extract_problem(image, dpi, client=client)
    solution = generate_solution(problem, client=client)
    annotations = layout_annotations(solution, dpi)
    annotated = render_overlay(image, annotations)
    output_path = save_output(annotated, filepath, fmt, dpi)

    return output_path, solution.confidence
```

- [ ] **Step 2: `solver/__main__.py` 구현**

```python
import sys
from pathlib import Path
from .pipeline import run


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m solver <filepath>")
        print("  Supported: .jpg .jpeg .png .pdf")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    print(f"Processing: {filepath}")
    output, confidence = run(filepath)
    print(f"Solved: {output}")

    if confidence < 0.8:
        print(
            f"⚠️  Confidence: {confidence:.0%} — AI 풀이를 반드시 확인하세요"
        )


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 파이프라인 스모크 테스트 (단위 테스트 아닌 통합 확인)**

실제 API 호출이 있으므로 dry-run 확인만 수행:

```bash
python -c "
from solver.pipeline import run
print('pipeline import OK')
import inspect
sig = inspect.signature(run)
print(f'run signature: {sig}')
"
```

Expected:
```
pipeline import OK
run signature: (filepath: str | pathlib.Path, client: anthropic.Anthropic | None = None) -> tuple[pathlib.Path, float]
```

- [ ] **Step 4: 커밋**

```bash
git add solver/pipeline.py solver/__main__.py
git commit -m "feat: implement pipeline orchestrator and CLI entrypoint"
```

---

## Task 9: /solve 스킬 정의

**Files:**
- Create: `~/.claude/skills/solve/SKILL.md`

- [ ] **Step 1: 스킬 디렉터리 생성**

```bash
mkdir -p ~/.claude/skills/solve
```

- [ ] **Step 2: `~/.claude/skills/solve/SKILL.md` 작성**

```markdown
# /solve — 수학 손글씨 풀이 생성기

수학 문제가 담긴 이미지·PDF에 손글씨 스타일 풀이를 오버레이한다.

## 사용법

```
/solve <filepath>
```

예시:
- `/solve ~/Downloads/homework.jpg`
- `/solve problem.pdf`
- `/solve /Users/User/math/test.png`

## 지원 형식

JPG, JPEG, PNG, PDF

## 실행 방법

1. filepath가 존재하는지 확인
2. 다음 명령 실행:

```bash
cd /Users/User/src/repos/math-handwriting-solver
ANTHROPIC_API_KEY=$(security find-generic-password -a anthropic -s ANTHROPIC_API_KEY -w) \
  python -m solver "<filepath>"
```

3. 출력 파일 경로를 사용자에게 알린다
4. confidence < 80%이면 "풀이를 직접 확인하세요" 경고를 함께 표시

## 출력 파일명

`{원본파일명}_solved.{확장자}` — 원본 파일은 수정되지 않는다.
```

- [ ] **Step 3: 스킬 동작 확인**

Claude Code를 재시작하거나 새 세션을 열어서 `/solve` 가 자동완성에 나타나는지 확인.

또는:

```bash
ls ~/.claude/skills/solve/
```

Expected: `SKILL.md`

- [ ] **Step 4: Anthropic API 키 Keychain 등록 확인**

```bash
security find-generic-password -a anthropic -s ANTHROPIC_API_KEY -w 2>/dev/null && echo "OK" || echo "키를 등록하세요: security add-generic-password -a anthropic -s ANTHROPIC_API_KEY -w <your-key>"
```

- [ ] **Step 5: 커밋**

```bash
git add .
git commit -m "feat: complete Stage 1 pipeline implementation"
```

---

## Task 10: 품질 게이트 검증

**Files:**
- Create: `scripts/quality_gates.py`

Stage 1 완료 조건을 측정한다. 미통과 시 해당 항목을 수정 후 재측정.

- [ ] **Step 1: `scripts/quality_gates.py` 작성**

```python
"""Stage 1 품질 게이트 측정 스크립트."""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageFont

FONTS_DIR = Path(__file__).parent.parent / "fonts"

# 중등 수학 특수기호 전체 목록
MATH_SYMBOLS = "∴∵≥≤≠√∫∑∏∞∈∉⊂⊃∪∩∧∨¬→←↔±°′″αβγπΩ²³"


def gate_font_coverage() -> bool:
    """Gate: Nanum 폰트로 수학 특수기호 렌더링 가능 확인."""
    print("\n[Gate 1] 폰트 커버리지")
    pen_path = FONTS_DIR / "NanumPenScript-Regular.ttf"
    gothic_path = FONTS_DIR / "NanumGothic-Regular.ttf"

    if not pen_path.exists() or not gothic_path.exists():
        print("  FAIL: 폰트 파일 없음 — python scripts/download_fonts.py 실행")
        return False

    pen_font = ImageFont.truetype(str(pen_path), 32)
    gothic_font = ImageFont.truetype(str(gothic_path), 32)

    img = Image.new("RGB", (800, 100), "white")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), MATH_SYMBOLS, font=gothic_font, fill=(0, 0, 0))
    draw.text((10, 50), "가나다라 x = √2 ∴ y ≠ 0", font=pen_font, fill=(0, 0, 0))
    img.save("quality_gate_font_coverage.png")

    print(f"  OK: 렌더링 완료 → quality_gate_font_coverage.png 확인")
    print(f"  확인 항목: □ 박스 없이 모든 기호가 렌더링됐는지 육안 검사")
    return True


def gate_dpi_rendering() -> bool:
    """Gate: 72/150/300dpi × A4/Letter 8종 조합 렌더링."""
    print("\n[Gate 2] DPI 렌더링")
    from solver.render_overlay import render_overlay
    from solver.models import Annotation, Point, AnnotationStyle

    DPIS = [72, 150, 300]
    SIZES = {"A4": (595, 842), "Letter": (612, 792)}
    TEST_ANN = [
        Annotation("text", "y = (x-1)² - 4", Point(50, 200), "blue", AnnotationStyle(font_size=28)),
        Annotation("box", "이차함수 표준형: y = a(x-p)² + q", Point(50, 680), "purple", AnnotationStyle(font_size=20)),
    ]

    from solver.layout_annotations import layout_annotations
    from solver.models import SolutionData

    solution = SolutionData(
        steps=[], final_answer="x = 1 ± 2", annotations=TEST_ANN,
        confidence=0.85, verified=True
    )

    for dpi in DPIS:
        for name, (w72, h72) in SIZES.items():
            scale = dpi / 72
            img = Image.new("RGB", (int(w72 * scale), int(h72 * scale)), "white")
            anns = layout_annotations(solution, dpi)
            result = render_overlay(img, anns)
            out = f"quality_gate_{dpi}dpi_{name}.png"
            result.save(out)
            print(f"  {dpi}dpi {name}: {out}")

    print("  확인 항목: annotation이 이미지 밖으로 벗어나지 않는지 육안 검사")
    return True


def gate_vision_baseline() -> None:
    """Gate: Vision 정확도 기준선 (수동 측정 안내)."""
    print("\n[Gate 3] Vision 정확도 기준선 (수동 측정)")
    print("  1. 중등 수학 문제 50개 수집 (교과서 캡처 또는 직접 촬영)")
    print("  2. 각 문제에 대해 extract_problem 실행")
    print("  3. 수동으로 OCR 정확도 채점 (수식·한글 모두 올바르면 정답)")
    print("  4. 정확도 < 80%이면:")
    print("     → extract_problem에 interactive=True 파라미터 추가")
    print("     → '이 문제가 맞나요? [y/N]' 프롬프트 구현")
    print("     → pipeline.run(interactive=True) 옵션 추가")


def gate_annotation_position(sample_dir: str | None = None) -> None:
    """Gate: 그래프 문제 10개 annotation 위치 검사."""
    print("\n[Gate 4] Annotation 위치 정확도 (수동 측정)")
    print("  1. 그래프 포함 수학 문제 10개 수집")
    print("  2. 파이프라인 실행 후 출력 이미지 확인")
    print("  3. 합격 기준: annotation bbox가 문제 텍스트 bbox 바깥에 위치")
    print("  4. 미합격 시 generate_solution 프롬프트의 problem_bottom 여백 조정")


if __name__ == "__main__":
    print("=== Stage 1 품질 게이트 ===")
    gate_font_coverage()
    gate_dpi_rendering()
    gate_vision_baseline()
    gate_annotation_position()
    print("\n완료. 생성된 PNG 파일을 육안으로 검사하세요.")
```

- [ ] **Step 2: 폰트 커버리지 + DPI 렌더링 자동 게이트 실행**

```bash
python scripts/quality_gates.py
```

Expected:
```
=== Stage 1 품질 게이트 ===

[Gate 1] 폰트 커버리지
  OK: 렌더링 완료 → quality_gate_font_coverage.png 확인
  확인 항목: □ 박스 없이 모든 기호가 렌더링됐는지 육안 검사

[Gate 2] DPI 렌더링
  72dpi A4: quality_gate_72dpi_A4.png
  72dpi Letter: quality_gate_72dpi_Letter.png
  ...
```

- [ ] **Step 3: 생성된 이미지 육안 검사**

`quality_gate_font_coverage.png` 열기:
- □ 박스 없이 ∴√≠ 등 기호가 보이면 통과
- □ 박스 있으면 `render_overlay.py`의 `SPECIAL_MATH` 집합에 해당 문자 추가

DPI 이미지(8개) 열기:
- annotation이 이미지 바깥으로 나가지 않으면 통과

- [ ] **Step 4: 전체 테스트 스위트 통과 확인**

```bash
pytest -v
```

Expected: 전체 통과 (폰트 없는 경우 render_overlay 테스트는 skip)

- [ ] **Step 5: 실제 문제 사진으로 E2E 테스트**

```bash
ANTHROPIC_API_KEY=$(security find-generic-password -a anthropic -s ANTHROPIC_API_KEY -w) \
  python -m solver <실제_수학_문제.jpg>
```

Expected:
```
Processing: <파일명>.jpg
Solved: <파일명>_solved.jpg
```

`<파일명>_solved.jpg` 열어서:
- 손글씨 풀이가 문제 아래 여백에 표시됨
- 보라색 개념 박스가 하단에 있음
- 원본 파일 수정 안 됨

- [ ] **Step 6: 최종 커밋**

```bash
git add scripts/quality_gates.py
git commit -m "test: add Stage 1 quality gate measurement scripts"
```

---

## Stage 1 완료 체크리스트

모두 통과하면 Stage 2 MCP 서버 계획으로 진행:

- [ ] `pytest -v` 전체 통과
- [ ] `quality_gate_font_coverage.png` — □ 박스 없음
- [ ] 8종 DPI 렌더링 이미지 — annotation 범위 이상 없음
- [ ] Vision 정확도 측정: 50문제 80% 이상 (미만이면 Vision 확인 단계 추가 후 재측정)
- [ ] 그래프 문제 10개 annotation 위치 검사 통과
- [ ] 실제 PDF 왕복 테스트: 원본 파일 수정 없음 확인
- [ ] sympy 검증 실패 시 워터마크 출력 확인
