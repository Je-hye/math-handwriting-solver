"""Generate example images that mimic an exam sheet with handwritten solution overlay."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).parent.parent
FONTS_DIR = REPO / "fonts"
OUT_DIR = REPO / "docs" / "examples"

PEN = str(FONTS_DIR / "NanumPenScript-Regular.ttf")
GOTHIC = str(FONTS_DIR / "NanumGothic-Regular.ttf")

W, H = 820, 980
BG = (252, 252, 248)
BLACK = (20, 20, 20)
GRAY = (150, 150, 150)
LIGHT_GRAY = (210, 210, 210)

# Original color scheme
BLUE = (30, 100, 200)
RED = (200, 40, 40)
GREEN = (40, 160, 40)
ORANGE = (210, 110, 20)
PURPLE = (120, 40, 180)

# Highlighter colors (semi-transparent)
HL_YELLOW = (255, 240, 0, 90)
HL_GREEN = (120, 255, 120, 80)


def j(x, y, amt=2):
    return x + random.randint(-amt, amt), y + random.randint(-amt, amt)


def highlight(img, x1, y1, x2, y2, color=HL_YELLOW):
    """Draw a semi-transparent highlighter band."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([x1, y1, x2, y2], fill=color)
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def make_input():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    g_sm = ImageFont.truetype(GOTHIC, 14)
    g_md = ImageFont.truetype(GOTHIC, 17)
    g_lg = ImageFont.truetype(GOTHIC, 19)
    g_q = ImageFont.truetype(GOTHIC, 16)

    # Header band
    draw.rectangle([0, 0, W, 52], fill=(235, 235, 235))
    draw.line([(0, 52), (W, 52)], fill=LIGHT_GRAY, width=1)
    draw.text((22, 16), "2025년 1학기 내신 기출", font=g_md, fill=BLACK)
    draw.text((W - 230, 16), "이차방정식의 풀이", font=g_md, fill=BLACK)

    # Question number and text
    draw.text((22, 68), "1.", font=g_lg, fill=BLACK)
    draw.text((46, 68), "이차방정식  x² - 3x - 10 = 0  의 두 근 중 큰 값은?  [3점]", font=g_q, fill=BLACK)

    # Answer choices
    choices = [("①", "-5"), ("②", "-2"), ("③", "2"), ("④", "5"), ("⑤", "7")]
    cx = [46, 178, 318, 452, 588]
    for (num, val), x in zip(choices, cx):
        draw.text((x, 112), num + " " + val, font=g_q, fill=BLACK)

    # Category tags
    draw.text((46, 148), "[중단원] 이차방정식의 풀이", font=g_sm, fill=GRAY)
    draw.text((46, 165), "[난이도] 하", font=g_sm, fill=GRAY)

    # Divider
    draw.line([(22, 195), (W - 22, 195)], fill=LIGHT_GRAY, width=1)

    # Solution area label
    draw.text((22, 208), "[풀이]", font=g_sm, fill=GRAY)

    return img, cx


def make_output(input_img, choice_x):
    img = input_img.copy()

    # --- 형광펜: 문제 핵심 수식에 노란 하이라이트 ---
    img = highlight(img, 142, 63, 390, 84, HL_YELLOW)   # x² - 3x - 10 = 0
    # 정답 라인에 초록 하이라이트 (나중에 ∴ 줄)
    img = highlight(img, 42, 432, 420, 460, HL_GREEN)

    draw = ImageDraw.Draw(img)

    pen_hd = ImageFont.truetype(PEN, 32)
    pen = ImageFont.truetype(PEN, 38)
    pen_sm = ImageFont.truetype(PEN, 28)

    # Solution header
    draw.text(j(22, 210, 1), "#풀이", font=pen_hd, fill=BLACK)

    # Factoring guide numbers (orange — 곱해서 -10, 더해서 -3 인 두 수)
    # Shown to the right of the first equation as a hint
    draw.text(j(390, 252, 1), "(-5) + (2) = -3", font=pen_sm, fill=ORANGE)
    draw.text(j(390, 280, 1), "(-5) x (2) = -10", font=pen_sm, fill=ORANGE)

    # Main solution steps (blue — 계산 과정)
    # x^2 notation used (NanumPenScript has no ² glyph)
    steps = [
        ("x^2 - 3x - 10 = 0", 260),
        ("(x + 2)(x - 5) = 0", 320),
        ("x = -2  or  x = 5", 380),
    ]
    for text, y in steps:
        draw.text(j(60, y, 2), text, font=pen, fill=BLUE)

    # Final answer (blue). Draw checkmark manually (green)
    draw.text(j(60, 438, 2), ".. 큰 값  a = 5", font=pen, fill=BLUE)

    # Hand-drawn green checkmark (two lines)
    cx_ck, cy_ck = 32, 450
    draw.line([(cx_ck, cy_ck), (cx_ck + 8, cy_ck + 10)], fill=GREEN, width=3)
    draw.line([(cx_ck + 8, cy_ck + 10), (cx_ck + 22, cy_ck - 8)], fill=GREEN, width=3)

    # Red circle around answer ④ 5 (red — 강조)
    ax = choice_x[3] + 14
    ay = 119
    draw.ellipse([ax - 22, ay - 14, ax + 22, ay + 18], outline=RED, width=3)

    # Purple concept box (purple — 핵심 개념)
    box_y = 510
    draw.rectangle([22, box_y, W - 22, box_y + 95], outline=PURPLE, width=2)
    draw.text(j(36, box_y + 8, 1), "[ 핵심 개념 ]", font=pen_sm, fill=PURPLE)
    concepts = [
        "x^2 + bx + c = 0 의 인수분해 : 합이 b, 곱이 c 인 두 수 p, q 를 찾아 (x+p)(x+q) = 0",
        "두 근의 합 : -b/a,   두 근의 곱 : c/a   (근과 계수의 관계)",
    ]
    for i, line in enumerate(concepts):
        draw.text(j(36, box_y + 38 + i * 30, 1), line, font=pen_sm, fill=PURPLE)

    return img


def main():
    random.seed(42)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    inp, choice_x = make_input()
    inp.save(OUT_DIR / "input.png")
    print(f"Saved {OUT_DIR / 'input.png'}")

    out = make_output(inp, choice_x)
    out.save(OUT_DIR / "output.png")
    print(f"Saved {OUT_DIR / 'output.png'}")


if __name__ == "__main__":
    main()
