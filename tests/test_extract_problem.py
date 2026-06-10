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
