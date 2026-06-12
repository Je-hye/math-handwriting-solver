"""Generate example images for docs/examples/ without API calls."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).parent.parent
FONTS_DIR = REPO / "fonts"
OUT_DIR = REPO / "docs" / "examples"

PEN_FONT = str(FONTS_DIR / "NanumPenScript-Regular.ttf")

W, H = 800, 780
BG = (255, 255, 250)
BLACK = (30, 30, 30)
BLUE = (30, 100, 200)
RED = (200, 40, 40)
GREEN = (40, 160, 40)
PURPLE = (120, 40, 180)


def jitter(x, y, amt=2):
    return x + random.randint(-amt, amt), y + random.randint(-amt, amt)


def make_input():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    font_big = ImageFont.truetype(PEN_FONT, 64)
    font_label = ImageFont.truetype(PEN_FONT, 22)

    problem = "2x + 3 = 7"
    draw.text(jitter(120, 140, 3), problem, font=font_big, fill=BLACK)
    draw.rectangle([100, 120, 500, 240], outline=(180, 180, 180), width=2)
    draw.text((100, 90), "수학 문제", font=font_label, fill=(120, 120, 120))

    return img


def make_output(input_img):
    img = input_img.copy()
    draw = ImageDraw.Draw(img)

    font_pen = ImageFont.truetype(PEN_FONT, 40)
    font_pen_sm = ImageFont.truetype(PEN_FONT, 30)
    font_pen_note = ImageFont.truetype(PEN_FONT, 26)
    font_pen_lg = ImageFont.truetype(PEN_FONT, 48)
    font_pen_concept = ImageFont.truetype(PEN_FONT, 24)

    steps = [
        ("2x + 3 = 7", ""),
        ("2x = 7 - 3", "← 양변에서 3을 뺀다"),
        ("2x = 4", ""),
        ("x = 2", "← 양변을 2로 나눈다"),
    ]

    y = 290
    for expr, note in steps:
        draw.text(jitter(140, y, 2), expr, font=font_pen, fill=BLUE)
        if note:
            draw.text(jitter(340, y + 4, 1), note, font=font_pen_note, fill=BLUE)
        y += 58

    # Green checkmark next to final answer
    draw.text(jitter(108, y - 58, 2), "✓", font=font_pen_lg, fill=GREEN)

    # Red answer label
    draw.text(jitter(140, y + 8, 2), "정답: x = 2", font=font_pen_sm, fill=RED)

    # Purple concept box — below solution, propositional form
    box_top = y + 60
    box_bot = y + 155
    draw.rectangle([100, box_top, 680, box_bot], outline=PURPLE, width=2)
    draw.text((112, box_top + 8), "[ 핵심 개념 ]", font=font_pen_concept, fill=PURPLE)
    concepts = [
        "등식의 성질: 등식의 양변에 같은 수를 더하거나 빼도 등식은 성립한다.",
        "등식의 성질: 등식의 양변에 같은 수를 곱하거나 나누어도 등식은 성립한다.",
    ]
    for i, line in enumerate(concepts):
        draw.text(jitter(112, box_top + 36 + i * 30, 1), line, font=font_pen_concept, fill=PURPLE)

    return img


def main():
    random.seed(42)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    inp = make_input()
    inp.save(OUT_DIR / "input.png")
    print(f"Saved {OUT_DIR / 'input.png'}")

    out = make_output(inp)
    out.save(OUT_DIR / "output.png")
    print(f"Saved {OUT_DIR / 'output.png'}")


if __name__ == "__main__":
    main()
