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
