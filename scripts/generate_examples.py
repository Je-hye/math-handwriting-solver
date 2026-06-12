"""Generate example images for docs/examples/ without API calls."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).parent.parent
FONTS_DIR = REPO / "fonts"
OUT_DIR = REPO / "docs" / "examples"

PEN_FONT = str(FONTS_DIR / "NanumPenScript-Regular.ttf")
GOTHIC_FONT = str(FONTS_DIR / "NanumGothic-Regular.ttf")

W, H = 800, 600
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
    font_label = ImageFont.truetype(GOTHIC_FONT, 16)

    # Problem text
    problem = "2x + 3 = 7"
    draw.text(jitter(120, 140, 3), problem, font=font_big, fill=BLACK)

    # Problem box
    draw.rectangle([100, 120, 500, 240], outline=(180, 180, 180), width=2)

    # Label
    draw.text((100, 90), "수학 문제", font=font_label, fill=(120, 120, 120))

    return img


def make_output(input_img):
    img = input_img.copy()
    draw = ImageDraw.Draw(img)

    font_pen = ImageFont.truetype(PEN_FONT, 40)
    font_pen_sm = ImageFont.truetype(PEN_FONT, 28)
    font_gothic_sm = ImageFont.truetype(GOTHIC_FONT, 14)
    font_pen_lg = ImageFont.truetype(PEN_FONT, 48)

    steps = [
        ("2x + 3 = 7", ""),
        ("2x = 7 - 3", "양변에서 3을 뺀다"),
        ("2x = 4", ""),
        ("x = 2", "양변을 2로 나눈다"),
    ]

    y = 290
    for i, (expr, note) in enumerate(steps):
        x = 140
        draw.text(jitter(x, y, 2), expr, font=font_pen, fill=BLUE)
        if note:
            draw.text((x + 220, y + 6), note, font=font_gothic_sm, fill=(80, 80, 200))
        y += 56

    # Purple concept box around "x = 2"
    box_y = y - 56
    draw.rectangle([130, box_y - 4, 270, box_y + 44], outline=PURPLE, width=3)
    draw.text((280, box_y + 4), "핵심", font=font_gothic_sm, fill=PURPLE)

    # Green checkmark
    draw.text(jitter(300, box_y, 2), "✓", font=font_pen_lg, fill=GREEN)

    # Red answer label
    draw.text(jitter(140, y + 10, 2), "정답: x = 2", font=font_pen_sm, fill=RED)

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
