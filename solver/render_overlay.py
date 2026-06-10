from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from .models import Annotation

FONTS_DIR = Path(__file__).parent.parent / "fonts"

COLOR_MAP = {
    "blue":   (26,  68,  204),
    "red":    (204, 51,  0),
    "green":  (34,  136, 68),
    "orange": (204, 102, 0),
    "purple": (102, 0,   153),
}

# 이 문자들은 NanumPenScript에 글리프 없음 → NanumGothic으로 폴백
SPECIAL_MATH = set("∴∵≥≤≠√∫∑∏∞∈∉⊂⊃∪∩∧∨¬→←↔±°′″")

_pen_cache: dict[int, ImageFont.FreeTypeFont] = {}
_gothic_cache: dict[int, ImageFont.FreeTypeFont] = {}


def _pen_font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _pen_cache:
        _pen_cache[size] = ImageFont.truetype(
            str(FONTS_DIR / "NanumPenScript-Regular.ttf"), size
        )
    return _pen_cache[size]


def _gothic_font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _gothic_cache:
        _gothic_cache[size] = ImageFont.truetype(
            str(FONTS_DIR / "NanumGothic-Regular.ttf"), size
        )
    return _gothic_cache[size]


def _choose_font(text: str, size: int) -> ImageFont.FreeTypeFont:
    if any(c in SPECIAL_MATH for c in text):
        return _gothic_font(size)
    return _pen_font(size)


def render_overlay(image: Image.Image, annotations: list[Annotation]) -> Image.Image:
    canvas = image.copy().convert("RGBA")
    for ann in annotations:
        _draw(canvas, ann)
    return canvas.convert("RGB")


def _draw(canvas: Image.Image, ann: Annotation) -> None:
    rgb = COLOR_MAP[ann.color]
    alpha = int(ann.style.opacity * 255)
    rgba = (*rgb, alpha)
    font = _choose_font(ann.content, ann.style.font_size)
    x, y = int(ann.position.x), int(ann.position.y)
    rot = ann.style.rotation_deg

    if ann.type == "box":
        _draw_concept_box(canvas, ann.content, x, y, font, rgba)
    elif ann.type == "circle":
        _draw_circle(canvas, x, y, rgba)
    elif ann.type == "underline":
        _draw_underline(canvas, ann.content, x, y, font, rgba, rot)
    else:
        # text, checkmark, arrow
        content = "✓" if ann.type == "checkmark" else ann.content
        _draw_rotated_text(canvas, content, x, y, font, rgba, rot)


def _draw_rotated_text(
    canvas: Image.Image,
    text: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    rgba: tuple[int, int, int, int],
    rotation_deg: float,
) -> None:
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = dummy.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0] + 10, bb[3] - bb[1] + 10

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((5, 5), text, font=font, fill=rgba)

    if rotation_deg:
        layer = layer.rotate(-rotation_deg, expand=True)

    canvas.paste(layer, (x, y), layer)


def _draw_concept_box(
    canvas: Image.Image,
    content: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    rgba: tuple[int, int, int, int],
) -> None:
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = dummy.textbbox((0, 0), content, font=font)
    w, h = bb[2] - bb[0] + 20, bb[3] - bb[1] + 16

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([x, y, x + w, y + h], outline=rgba, width=2)
    draw.text((x + 10, y + 8), content, font=font, fill=rgba)


def _draw_circle(
    canvas: Image.Image,
    cx: int,
    cy: int,
    rgba: tuple[int, int, int, int],
    r: int = 30,
) -> None:
    ImageDraw.Draw(canvas).ellipse(
        [cx - r, cy - r, cx + r, cy + r], outline=rgba, width=2
    )


def _draw_underline(
    canvas: Image.Image,
    content: str,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    rgba: tuple[int, int, int, int],
    rotation_deg: float,
) -> None:
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = dummy.textbbox((0, 0), content, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]

    draw = ImageDraw.Draw(canvas)
    draw.text((x, y), content, font=font, fill=rgba)
    draw.line([x, y + h + 2, x + w, y + h + 2], fill=rgba, width=2)
