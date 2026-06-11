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
