import pytest
from pathlib import Path
from PIL import Image
from solver.save_output import save_output


def test_jpeg_output_named_with_solved_suffix(tmp_path):
    img = Image.new("RGB", (100, 100))
    src = tmp_path / "problem.jpg"
    img.save(str(src))

    out = save_output(img, src, ".jpg")

    assert out.name == "problem_solved.jpg"
    assert out.exists()


def test_png_output_preserves_extension(tmp_path):
    img = Image.new("RGB", (100, 100))
    src = tmp_path / "hw.png"
    img.save(str(src))

    out = save_output(img, src, ".png")

    assert out.name == "hw_solved.png"


def test_output_not_same_path_as_source(tmp_path):
    img = Image.new("RGB", (100, 100))
    src = tmp_path / "problem.jpg"
    img.save(str(src))

    out = save_output(img, src, ".jpg")

    assert out != src


def test_original_file_content_unchanged(tmp_path):
    original = Image.new("RGB", (100, 100), color=(255, 0, 0))
    src = tmp_path / "problem.jpg"
    original.save(str(src))
    original_mtime = src.stat().st_mtime

    modified = Image.new("RGB", (100, 100), color=(0, 0, 255))
    save_output(modified, src, ".jpg")

    assert src.stat().st_mtime == original_mtime


def test_output_is_valid_image(tmp_path):
    img = Image.new("RGB", (595, 842), color=(200, 200, 200))
    src = tmp_path / "problem.jpg"
    img.save(str(src))

    out = save_output(img, src, ".jpg")

    loaded = Image.open(str(out))
    assert loaded.size == (595, 842)
