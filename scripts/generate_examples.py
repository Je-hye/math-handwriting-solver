"""Generate example images that mimic an exam sheet with handwritten solution overlay."""
from pathlib import Path
import re
import random
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).parent.parent
FONTS_DIR = REPO / "fonts"
OUT_DIR = REPO / "docs" / "examples"

PEN   = str(FONTS_DIR / "NanumPenScript-Regular.ttf")
GOTHIC = str(FONTS_DIR / "NanumGothic-Regular.ttf")

W, H = 820, 980
BG         = (252, 252, 248)
BLACK      = (20, 20, 20)
GRAY       = (150, 150, 150)
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


def draw_math(draw, x, y, text, font, sup_font, fill):
    """Draw math text; ^ marks superscript. No per-token jitter — call jit() before this."""
    sup_offset = int(font.size * 0.40)
    cursor = x
    for tok in re.split(r'(\^[0-9a-zA-Z]+)', text):
        if tok.startswith('^'):
            sup = tok[1:]
            draw.text((int(cursor), y - sup_offset), sup, font=sup_font, fill=fill)
            cursor += draw.textlength(sup, font=sup_font) + 1
        else:
            draw.text((int(cursor), y), tok, font=font, fill=fill)
            cursor += draw.textlength(tok, font=font)
    return int(cursor)


def draw_choice(draw, x, y, n, label, font, fill):
    """Draw a circled number + label. Returns x after the item."""
    text = str(n)
    tw = int(draw.textlength(text, font=font))
    th = font.size
    r  = max(tw, th) // 2 + 4
    cx, cy = x + r, y + th // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fill, width=1)
    draw.text((cx - tw // 2, y), text, font=font, fill=fill)
    lx = x + 2 * r + 4
    draw.text((lx, y), " " + label, font=font, fill=fill)
    return lx + int(draw.textlength(" " + label, font=font))


# ────────────────────────────────────────────────────────────
def make_input():
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    g_sm  = ImageFont.truetype(GOTHIC, 14)
    g_md  = ImageFont.truetype(GOTHIC, 17)
    g_lg  = ImageFont.truetype(GOTHIC, 19)
    g_q   = ImageFont.truetype(GOTHIC, 16)
    g_sup = ImageFont.truetype(GOTHIC, 11)

    # ── Header ──────────────────────────────────────────────
    draw.rectangle([0, 0, W, 52], fill=(235, 235, 235))
    draw.line([(0, 52), (W, 52)], fill=LIGHT_GRAY, width=1)
    draw.text((22, 16), "2025년 1학기 내신 기출", font=g_md, fill=BLACK)
    draw.text((W - 230, 16), "이차방정식의 풀이", font=g_md, fill=BLACK)

    # ── Question ────────────────────────────────────────────
    draw.text((22, 68), "1.", font=g_lg, fill=BLACK)
    # Measure prefix to know where the equation starts for highlighter
    prefix   = "이차방정식  "
    eq_str   = "x^2 - 3x - 10 = 0"
    suffix   = "  의 두 근 중 큰 값은?  [3점]"
    hl_x1    = 46 + int(draw.textlength(prefix, font=g_q)) - 2
    hl_x2    = hl_x1 + int(draw.textlength(
                   re.sub(r'\^[0-9a-zA-Z]+', '', eq_str), font=g_q)) + 14
    qx = draw_math(draw, 46, 68, prefix + eq_str + suffix, g_q, g_sup, BLACK)

    # ── Answer choices (circled numbers drawn manually) ─────
    CHOICE_Y = 112
    choices  = [("-5", 46), ("-2", 190), ("2", 334), ("5", 470), ("7", 610)]
    for i, (label, cx) in enumerate(choices, 1):
        draw_choice(draw, cx, CHOICE_Y, i, label, g_q, BLACK)

    # ── Tags ────────────────────────────────────────────────
    draw.text((46, 152), "[중단원] 이차방정식의 풀이", font=g_sm, fill=GRAY)
    draw.text((46, 170), "[난이도] 하",               font=g_sm, fill=GRAY)

    draw.line([(22, 198), (W - 22, 198)], fill=LIGHT_GRAY, width=1)
    draw.text((22, 210), "[풀이]", font=g_sm, fill=GRAY)

    return img, hl_x1, hl_x2


def make_output(input_img, hl_x1, hl_x2):
    # ── Highlights ──────────────────────────────────────────
    # Yellow: key equation in the question (position computed dynamically)
    img = highlight(input_img, hl_x1, 60, hl_x2, 86, HL_YELLOW)
    # Green: final answer line (y pre-computed below = 438)
    img = highlight(img, 42, 430, 450, 462, HL_GREEN)

    draw = ImageDraw.Draw(img)

    pen     = ImageFont.truetype(PEN, 38)
    pen_hd  = ImageFont.truetype(PEN, 32)
    pen_sm  = ImageFont.truetype(PEN, 27)
    pen_sup = ImageFont.truetype(PEN, 24)

    g_q   = ImageFont.truetype(GOTHIC, 16)   # reused for circle re-draw

    # ── Solution header ─────────────────────────────────────
    draw.text(jit(22, 212, 1), "#풀이", font=pen_hd, fill=BLACK)

    # ── Step 1 ──────────────────────────────────────────────
    sx, sy = jit(60, 264, 2)
    eq_end = draw_math(draw, sx, sy, "x^2 - 3x - 10 = 0", pen, pen_sup, BLUE)

    # Orange factoring hint: right of equation
    hx = eq_end + 20
    draw.text((hx,      sy - 2), "-5", font=pen_sm, fill=ORANGE)
    draw.text((hx, sy + 28),     "+2", font=pen_sm, fill=ORANGE)

    # ── Step 2 ──────────────────────────────────────────────
    draw_math(draw, *jit(60, 324, 2), "(x + 2)(x - 5) = 0", pen, pen_sup, BLUE)

    # ── Step 3 ──────────────────────────────────────────────
    draw_math(draw, *jit(60, 384, 2), "x = -2  or  x = 5", pen, pen_sup, BLUE)

    # ── Final answer ────────────────────────────────────────
    draw_math(draw, *jit(60, 438, 2), "..  큰 값  a = 5", pen, pen_sup, BLUE)

    # Green checkmark (two lines)
    draw.line([(30, 450), (40, 462)], fill=GREEN, width=3)
    draw.line([(40, 462), (56, 442)], fill=GREEN, width=3)

    # ── Red circle on answer choice ④ 5 ─────────────────────
    # Choice ④ is at x=470. The circle in draw_choice has r≈12, center at 470+12=482
    ax, ay = 484, 120
    draw.ellipse([ax - 20, ay - 16, ax + 20, ay + 16], outline=RED, width=3)

    # ── Purple concept box (padding: 16px inside) ───────────
    pen_cs  = ImageFont.truetype(PEN, 24)
    pen_css = ImageFont.truetype(PEN, 17)
    PAD   = 16
    box_y = 510
    box_h = 110
    draw.rectangle([22, box_y, W - 22, box_y + box_h], outline=PURPLE, width=2)
    draw.text(jit(22 + PAD, box_y + PAD, 1),
              "[ 핵심 개념 ]", font=pen_cs, fill=PURPLE)
    draw_math(draw, *jit(22 + PAD, box_y + PAD + 34, 1),
              "x^2 + bx + c = 0 의 인수분해 : 합이 b, 곱이 c 인 두 수 p, q 로 (x+p)(x+q) = 0",
              pen_cs, pen_css, PURPLE)
    draw_math(draw, *jit(22 + PAD, box_y + PAD + 68, 1),
              "두 근의 합 : -b/a,   두 근의 곱 : c/a   (근과 계수의 관계)",
              pen_cs, pen_css, PURPLE)

    return img


def main():
    random.seed(42)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    inp, hl_x1, hl_x2 = make_input()
    inp.save(OUT_DIR / "input.png")
    print(f"Saved {OUT_DIR / 'input.png'}")

    out = make_output(inp, hl_x1, hl_x2)
    out.save(OUT_DIR / "output.png")
    print(f"Saved {OUT_DIR / 'output.png'}")


if __name__ == "__main__":
    main()
