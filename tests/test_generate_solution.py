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
