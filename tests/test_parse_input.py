import pytest
from pathlib import Path
from PIL import Image
from solver.parse_input import parse_input


def test_parse_jpeg_returns_image_dpi_format(tmp_path):
    img = Image.new("RGB", (595, 842))
    path = tmp_path / "problem.jpg"
    img.save(str(path), dpi=(72, 72))

    result_img, dpi, fmt = parse_input(path)

    assert isinstance(result_img, Image.Image)
    assert result_img.mode == "RGB"
    assert dpi == 72
    assert fmt == ".jpg"


def test_parse_png_detected(tmp_path):
    img = Image.new("RGB", (200, 200))
    path = tmp_path / "test.png"
    img.save(str(path))

    _, _, fmt = parse_input(path)

    assert fmt == ".png"


def test_parse_image_no_dpi_metadata_defaults_to_72(tmp_path):
    img = Image.new("RGB", (100, 100))
    path = tmp_path / "nodpi.jpg"
    img.save(str(path))  # no dpi kwarg

    _, dpi, _ = parse_input(path)

    assert dpi == 72


def test_unsupported_format_raises_value_error(tmp_path):
    path = tmp_path / "file.bmp"
    path.write_bytes(b"BM fake bmp data")

    with pytest.raises(ValueError, match="Unsupported format"):
        parse_input(path)


def test_file_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_input(tmp_path / "nonexistent.jpg")
