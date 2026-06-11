from __future__ import annotations
from pathlib import Path
from PIL import Image
import fitz


def save_output(
    image: Image.Image,
    source_path: str | Path,
    original_format: str,
    dpi: int = 72,
) -> Path:
    """원본을 건드리지 않고 {stem}_solved{suffix}로 저장. 출력 경로를 반환."""
    src = Path(source_path)
    out = src.parent / f"{src.stem}_solved{src.suffix}"

    if out.resolve() == src.resolve():
        raise ValueError(f"Output {out} must not overwrite source {src}")

    if original_format == ".pdf":
        _save_as_pdf(image, out, dpi)
    else:
        image.save(str(out))

    return out


def _save_as_pdf(image: Image.Image, out_path: Path, dpi: int) -> None:
    import io
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=95)
    buf.seek(0)

    # 72dpi 기준 pt 크기로 페이지 생성
    pt_w = image.width * 72 / dpi
    pt_h = image.height * 72 / dpi

    doc = fitz.open()
    page = doc.new_page(width=pt_w, height=pt_h)
    page.insert_image(fitz.Rect(0, 0, pt_w, pt_h), stream=buf.read())
    doc.save(str(out_path))
    doc.close()
