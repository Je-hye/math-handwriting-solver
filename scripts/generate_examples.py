"""Generate example images that mimic an exam sheet with handwritten solution overlay."""
from pathlib import Path
import re
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

BLUE   = (30, 100, 200)
RED    = (200, 40, 40)
GREEN  = (40, 160, 40)
ORANGE = (210, 110, 20)
PURPLE = (120, 40, 180)

HL_YELLOW = (255, 240, 0, 90)
HL_GREEN  = (120, 255, 120, 80)


def jit(x, y, amt=2):
    return x + random.randint(-amt, amt), y + random.randint(-amt, amt)


def highlight(img, x1, y1, x2, y2, color):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle([x1, y1, x2, y2], fill=color)
    base = img.convert("RGBA")
    base.alpha_composite(overlay)
    return base.convert("RGB")


def math_width(draw, text, font, sup_font):
    """Measure pixel width of a math string that uses ^ for superscripts."""
    w = 0
    for tok in re.split(r'(\^[0-9a-zA-Z]+)', text):
        if tok.startswith('^'):
            w += draw.textlength(tok[1:], font=sup_font)
        else:
            w += draw.textlength(tok, font=font)
    return w


def draw_math(draw, x, y, text, font, sup_font, fill, jamt=0):
    """Draw math text with ^ rendered as raised superscript. Returns final x."""
    sup_offset = int(font.size * 0.42)   # how far up the superscript sits
    cursor = x
    for tok in re.split(r'(\^[0-9a-zA-Z]+)', text):
        if tok.startswith('^'):
            sup = tok[1:]
            jx, jy = jit(cursor, y - sup_offset, jamt)
            draw.text((jx, jy), sup, font=sup_font, fill=fill)
            cursor += draw.textlength(sup, font=sup_font) + 1
        else:
            jx, jy = jit(cursor, y, jamt)
            draw.text((jx, jy), tok, font=font, fill=fill)
            cursor += draw.textlength(tok, font=font)
    return cursor


# ──────────────────────────────────────────────
def make_input():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    g_sm  = ImageFont.truetype(GOTHIC, 14)
    g_md  = ImageFont.truetype(GOTHIC, 17)
    g_lg  = ImageFont.truetype(GOTHIC, 19)
    g_q   = ImageFont.truetype(GOTHIC, 16)
    g_sup = ImageFont.truetype(GOTHIC, 11)   # superscript for printed text

    # Header
    draw.rectangle([0, 0, W, 52], fill=(235, 235, 235))
    draw.line([(0, 52), (W, 52)], fill=LIGHT_GRAY, width=1)
    draw.text((22, 16), "2025년 1학기 내신 기출", font=g_md, fill=BLACK)
    draw.text((W - 230, 16), "이차방정식의 풀이", font=g_md, fill=BLACK)

    # Question number
    draw.text((22, 68), "1.", font=g_lg, fill=BLACK)

    # Question text with superscript rendered manually
    qx = 46
    qy = 68
    qx = draw_math(draw, qx, qy, "이차방정식  x^2 - 3x - 10 = 0  의 두 근 중 큰 값은?  [3점]",
                   g_q, g_sup, BLACK)

    # Answer choices — record x positions for circle later
    choices = [("①", "-5"), ("②", "-2"), ("③", "2"), ("④", "5"), ("⑤", "7")]
    cx_list = [46, 178, 318, 452, 588]
    for (num, val), cx in zip(choices, cx_list):
        draw.text((cx, 112), num + " " + val, font=g_q, fill=BLACK)

    draw.text((46, 148), "[중단원] 이차방정식의 풀이", font=g_sm, fill=GRAY)
    draw.text((46, 165), "[난이도] 하", font=g_sm, fill=GRAY)
    draw.line([(22, 195), (W - 22, 195)], fill=LIGHT_GRAY, width=1)
    draw.text((22, 208), "[풀이]", font=g_sm, fill=GRAY)

    return img, cx_list


def make_output(input_img, cx_list):
    # Yellow highlight on the equation in the question
    img = highlight(input_img, 144, 62, 382, 84, HL_YELLOW)
    # Green highlight on final answer line (added later; placeholder y used)
    img = highlight(img, 42, 430, 440, 460, HL_GREEN)

    draw = ImageDraw.Draw(img)

    pen    = ImageFont.truetype(PEN, 38)
    pen_hd = ImageFont.truetype(PEN, 32)
    pen_sm = ImageFont.truetype(PEN, 27)
    pen_sup = ImageFont.truetype(PEN, 24)    # superscript for handwriting

    # Solution header
    draw.text(jit(22, 210, 1), "#풀이", font=pen_hd, fill=BLACK)

    # ── Step 1: original equation ──────────────────────────────
    eq_end = draw_math(draw, *jit(60, 262, 2),
                       "x^2 - 3x - 10 = 0", pen, pen_sup, BLUE, jamt=2)

    # Orange factoring hint to the right (합이 -3, 곱이 -10인 두 수: -5, +2)
    hx = int(eq_end) + 24
    draw.text(jit(hx, 255, 1), "-5", font=pen_sm, fill=ORANGE)
    draw.text(jit(hx, 283, 1), "+2", font=pen_sm, fill=ORANGE)

    # ── Step 2: factored form ──────────────────────────────────
    draw_math(draw, *jit(60, 322, 2),
              "(x + 2)(x - 5) = 0", pen, pen_sup, BLUE, jamt=2)

    # ── Step 3: roots ─────────────────────────────────────────
    draw_math(draw, *jit(60, 382, 2),
              "x = -2  or  x = 5", pen, pen_sup, BLUE, jamt=2)

    # ── Final answer (highlighted line) ───────────────────────
    draw_math(draw, *jit(60, 437, 2),
              "..  큰 값  a = 5", pen, pen_sup, BLUE, jamt=2)

    # Green checkmark (drawn as two lines)
    draw.line([(30, 450), (40, 462)], fill=GREEN, width=3)
    draw.line([(40, 462), (56, 443)], fill=GREEN, width=3)

    # Red circle around ④ 5
    ax = cx_list[3] + 14
    draw.ellipse([ax - 22, 108, ax + 22, 132], outline=RED, width=3)

    # ── Purple concept box ────────────────────────────────────
    box_y = 510
    draw.rectangle([22, box_y, W - 22, box_y + 95], outline=PURPLE, width=2)
    draw.text(jit(36, box_y + 8, 1), "[ 핵심 개념 ]", font=pen_sm, fill=PURPLE)

    def cbox_math(x, y, text):
        draw_math(draw, *jit(x, y, 1), text, pen_sm,
                  ImageFont.truetype(PEN, 18), PURPLE, jamt=1)

    cbox_math(36, box_y + 38,
              "x^2 + bx + c = 0 의 인수분해 : 합이 b, 곱이 c 인 두 수 p, q 를 찾아 (x+p)(x+q) = 0")
    cbox_math(36, box_y + 68,
              "두 근의 합 : -b/a,   두 근의 곱 : c/a   (근과 계수의 관계)")

    return img


def main():
    random.seed(42)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    inp, cx_list = make_input()
    inp.save(OUT_DIR / "input.png")
    print(f"Saved {OUT_DIR / 'input.png'}")

    out = make_output(inp, cx_list)
    out.save(OUT_DIR / "output.png")
    print(f"Saved {OUT_DIR / 'output.png'}")


if __name__ == "__main__":
    main()
