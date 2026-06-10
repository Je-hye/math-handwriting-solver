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
