import io
import pytest
from PIL import Image
from solver.models import (
    ProblemData, SolutionData, Annotation, BoundingBox, Point, AnnotationStyle, Figure
)


def test_bounding_box_creation():
    """BoundingBox 생성 및 속성 검증"""
    bbox = BoundingBox(x=50, y=50, width=495, height=100)
    assert bbox.x == 50
    assert bbox.y == 50
    assert bbox.width == 495
    assert bbox.height == 100


def test_figure_creation():
    """Figure 생성 및 타입 검증"""
    bbox = BoundingBox(x=0, y=0, width=100, height=100)
    figure = Figure(type="graph", bbox=bbox)
    assert figure.type == "graph"
    assert figure.bbox == bbox


def test_point_creation():
    """Point 생성 및 좌표 검증"""
    point = Point(x=100.5, y=200.5)
    assert point.x == 100.5
    assert point.y == 200.5


def test_annotation_style_defaults():
    """AnnotationStyle 기본값 검증"""
    style = AnnotationStyle()
    assert style.rotation_deg == 0.0
    assert style.opacity == 0.9
    assert style.font_size == 24


def test_annotation_style_custom():
    """AnnotationStyle 커스텀 값 검증"""
    style = AnnotationStyle(rotation_deg=45.0, opacity=0.5, font_size=16)
    assert style.rotation_deg == 45.0
    assert style.opacity == 0.5
    assert style.font_size == 16


def test_annotation_creation():
    """Annotation 생성 및 기본값 검증"""
    position = Point(x=50, y=200)
    annotation = Annotation(
        type="circle",
        content="test",
        position=position,
        color="blue",
    )
    assert annotation.type == "circle"
    assert annotation.content == "test"
    assert annotation.position == position
    assert annotation.color == "blue"
    assert annotation.style.rotation_deg == 0.0


def test_annotation_with_custom_style():
    """Annotation에 커스텀 스타일 적용"""
    position = Point(x=50, y=200)
    custom_style = AnnotationStyle(rotation_deg=30.0, opacity=0.7, font_size=32)
    annotation = Annotation(
        type="text",
        content="custom",
        position=position,
        color="red",
        style=custom_style,
    )
    assert annotation.style.rotation_deg == 30.0
    assert annotation.style.opacity == 0.7
    assert annotation.style.font_size == 32


def test_problem_data_creation():
    """ProblemData 생성 및 필수 속성 검증"""
    # 간단한 JPEG 생성
    image = Image.new("RGB", (595, 842), color=(255, 255, 255))
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    raw_image_bytes = buf.getvalue()

    bbox = BoundingBox(x=50, y=50, width=495, height=100)
    problem = ProblemData(
        text="y = x² - 2x - 3을 풀어라",
        problem_type="equation",
        figures=[],
        bbox=bbox,
        raw_image=raw_image_bytes,
        image_width=595,
        image_height=842,
    )

    assert problem.text == "y = x² - 2x - 3을 풀어라"
    assert problem.problem_type == "equation"
    assert problem.figures == []
    assert problem.bbox == bbox
    assert isinstance(problem.raw_image, bytes)
    assert len(problem.raw_image) > 0
    assert problem.image_width == 595
    assert problem.image_height == 842


def test_problem_data_with_figures():
    """ProblemData with 여러 Figure 포함"""
    image = Image.new("RGB", (595, 842), color=(255, 255, 255))
    buf = io.BytesIO()
    image.save(buf, format="JPEG")

    bbox1 = BoundingBox(x=0, y=0, width=100, height=100)
    bbox2 = BoundingBox(x=100, y=0, width=100, height=100)
    figure1 = Figure(type="graph", bbox=bbox1)
    figure2 = Figure(type="geometry", bbox=bbox2)

    problem = ProblemData(
        text="problem",
        problem_type="graph",
        figures=[figure1, figure2],
        bbox=BoundingBox(x=50, y=50, width=500, height=700),
        raw_image=buf.getvalue(),
        image_width=595,
        image_height=842,
    )

    assert len(problem.figures) == 2
    assert problem.figures[0].type == "graph"
    assert problem.figures[1].type == "geometry"


def test_solution_data_creation():
    """SolutionData 생성 및 필수 속성 검증"""
    solution = SolutionData(
        steps=["step1", "step2"],
        final_answer="x = 3",
        annotations=[],
        confidence=0.85,
        verified=True,
    )

    assert solution.steps == ["step1", "step2"]
    assert solution.final_answer == "x = 3"
    assert solution.annotations == []
    assert solution.confidence == 0.85
    assert solution.verified is True


def test_solution_data_with_annotations():
    """SolutionData with 여러 Annotation 포함"""
    annotations = [
        Annotation(
            type="text",
            content="annotation1",
            position=Point(x=50, y=200),
            color="blue",
        ),
        Annotation(
            type="checkmark",
            content="✓",
            position=Point(x=50, y=300),
            color="green",
        ),
    ]

    solution = SolutionData(
        steps=["step1"],
        final_answer="answer",
        annotations=annotations,
        confidence=0.9,
        verified=True,
    )

    assert len(solution.annotations) == 2
    assert solution.annotations[0].type == "text"
    assert solution.annotations[1].type == "checkmark"
