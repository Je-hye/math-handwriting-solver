from __future__ import annotations
from pathlib import Path
from PIL import Image
import fitz  # pymupdf

SUPPORTED = {".jpg", ".jpeg", ".png", ".pdf"}
PDF_RENDER_DPI = 150


def parse_input(filepath: str | Path) -> tuple[Image.Image, int, str]:
    """Returns (rgb_image, dpi, suffix_lower)."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(
            f"Unsupported format: {suffix!r}. Supported: {sorted(SUPPORTED)}"
        )

    if suffix == ".pdf":
        return _parse_pdf(path)
    return _parse_image(path, suffix)


def _parse_image(path: Path, suffix: str) -> tuple[Image.Image, int, str]:
    img = Image.open(path)
    dpi_info = img.info.get("dpi", (72, 72))
    dpi = int(dpi_info[0]) if dpi_info[0] else 72
    return img.convert("RGB"), dpi, suffix


def _parse_pdf(path: Path) -> tuple[Image.Image, int, str]:
    doc = fitz.open(str(path))
    page = doc[0]
    mat = fitz.Matrix(PDF_RENDER_DPI / 72, PDF_RENDER_DPI / 72)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img, PDF_RENDER_DPI, ".pdf"
