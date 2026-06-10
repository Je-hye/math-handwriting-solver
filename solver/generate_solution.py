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
