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
