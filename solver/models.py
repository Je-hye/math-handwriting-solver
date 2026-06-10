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
