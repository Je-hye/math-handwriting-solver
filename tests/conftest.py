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
