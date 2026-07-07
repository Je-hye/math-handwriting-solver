"""
Generate example images: render exam PDF page, then overlay handwritten solution.
Usage: python scripts/generate_examples.py [path/to/exam.pdf]
"""
import sys
import math
import re
import random
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont

REPO      = Path(__file__).parent.parent
FONTS_DIR = REPO / "fonts"
OUT_DIR   = REPO / "docs" / "examples"
PEN       = str(FONTS_DIR / "NanumPenScript-Regular.ttf")

DEFAULT_PDF = Path("/Users/User/Downloads/[중][2025][3-1-기][수성구][황금중][비상][이차방정식의풀이-이차함수의활용] (작업).pdf")

# Render DPI
DPI   = 150
SCALE = DPI / 72  # 2.0833

# Original color scheme
BLUE   = (30, 100, 200)
RED    = (200, 40, 40)
GREEN  = (40, 160, 40)
ORANGE = (210, 110, 20)
PURPLE = (120, 40, 180)
BLACK  = (20, 20, 20)

HL_YELLOW = (255, 240, 0, 90)
HL_GREEN  = (120, 255, 120, 80)


# ── helpers ──────────────────────────────────────────────────────────────────

def jit(x, y, amt=2):
    return x + random.randint(-amt, amt), y + random.randint(-amt, amt)


def highlight(img, x1, y1, x2, y2, color):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([x1, y1, x2, y2], fill=color)
    base = img.convert("RGBA")
    base.alpha_composite(ov)
    return base.convert("RGB")


def hand_circle(draw, cx, cy, rx, ry, color, width=2):
    """Draw a wobbly, hand-drawn-looking ellipse."""
    N = 80
    pts = []
    # random low-frequency wobble phases (roughjs-style bezier perturbation)
    phase_x = random.uniform(0, 2 * math.pi)
    phase_y = random.uniform(0, 2 * math.pi)
    start   = random.uniform(-0.15, 0.15)   # random entry angle
    for i in range(N + 10):                 # overdraw 10pts for natural closure
        t = start + 2 * math.pi * i / N
        wobble_x = rx * 0.10 * math.sin(3 * t + phase_x)
        wobble_y = ry * 0.10 * math.cos(2 * t + phase_y)
        rr_x = rx + wobble_x + random.gauss(0, rx * 0.06)
        rr_y = ry + wobble_y + random.gauss(0, ry * 0.06)
        x = cx + rr_x * math.cos(t) + random.gauss(0, 1.8)
        y = cy + rr_y * math.sin(t) + random.gauss(0, 1.8)
        pts.append((int(x), int(y)))
    draw.line(pts, fill=color, width=width)


def draw_math(draw, x, y, text, font, sup_font, fill):
    """Render text; ^ prefix = superscript at smaller size and raised position."""
    sup_rise = int(font.size * 0.40)
    cursor = float(x)
    for tok in re.split(r'(\^[0-9a-zA-Z]+)', text):
        if tok.startswith('^'):
            sup = tok[1:]
            draw.text((int(cursor), y - sup_rise), sup, font=sup_font, fill=fill)
            cursor += draw.textlength(sup, font=sup_font) + 1
        else:
            draw.text((int(cursor), y), tok, font=font, fill=fill)
            cursor += draw.textlength(tok, font=font)
    return int(cursor)


# ── main steps ────────────────────────────────────────────────────────────────

def pdf_to_image(pdf_path, page_num=0):
    doc = fitz.open(str(pdf_path))
    page = doc[page_num]
    mat = fitz.Matrix(SCALE, SCALE)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def overlay_solution(base):
    """Overlay handwritten solution for problem #2 on the rendered page."""
    # Pixel positions extracted from PDF text layout at 150 DPI:
    # ④ answer choice: (762, 390)–(804, 413)  → center (783, 401)
    # Right column starts at x≈762, question at y≈178
    # [난이도] 하 ends at y≈479  → solution area starts below here

    # ── Yellow highlight on the equation in problem 2 ──────────────────────
    img = highlight(base, 875, 174, 1070, 210, HL_YELLOW)
    draw = ImageDraw.Draw(img)

    # Fonts — sized for 150 DPI page
    FS      = 26
    pen     = ImageFont.truetype(PEN, FS)
    pen_sup = ImageFont.truetype(PEN, int(FS * 0.60))
    pen_sm  = ImageFont.truetype(PEN, int(FS * 0.78))
    pen_hd  = ImageFont.truetype(PEN, int(FS * 1.1))

    LH  = int(FS * 1.70)   # line height
    SOL_X = 775             # x-start of solution
    y = 1250                # y-start: blank area below teacher's printed solution (~y≈1130)

    # ── #2 header ──────────────────────────────────────────────────────────
    draw.text(jit(750, y - 40, 2), "#2", font=pen_hd, fill=BLACK)

    # glyph metrics: NanumPenScript FS=26 → actual glyph top=2, bottom=22 (height 20px)
    GLYPH_H  = 20
    SM_H     = 16   # pen_sm (size 20) glyph height
    HINT_GAP = 10   # gap between equation bottom and first hint line

    # ── Equation 1: x^2 + 9x - 22 = 0 ────────────────────────────────────
    draw_math(draw, *jit(SOL_X, y, 2), "x^2 + 9x - 22 = 0", pen, pen_sup, BLUE)
    # Factoring hint (orange): clearly below the equation
    h_y = y + GLYPH_H + HINT_GAP
    draw.text(jit(SOL_X + 22, h_y, 1),                   "11", font=pen_sm, fill=ORANGE)
    draw.text(jit(SOL_X + 22, h_y + SM_H + 4, 1),        "-2", font=pen_sm, fill=ORANGE)

    y += int(LH * 2.0)   # room for two hint lines
    draw_math(draw, *jit(SOL_X, y, 2), "(x - 2)(x + 11) = 0", pen, pen_sup, BLUE)

    y += LH
    draw_math(draw, *jit(SOL_X, y, 2), "x = 2  or  x = -11", pen, pen_sup, BLUE)

    y += LH
    # Green highlight only on the answer value "a = 2"
    prefix1_w = int(draw.textlength(".. 큰 수  ", font=pen))
    ans1_val_w = pen.getbbox("a = 2")[2]
    img = highlight(img, SOL_X + prefix1_w - 2, y - 1,
                    SOL_X + prefix1_w + ans1_val_w + 6, y + GLYPH_H + 3, HL_GREEN)
    draw = ImageDraw.Draw(img)
    draw_math(draw, *jit(SOL_X, y, 2), ".. 큰 수  a = 2", pen, pen_sup, BLUE)

    # ── Equation 2: 2x^2 + 5x - 3 = 0 ────────────────────────────────────
    y += int(LH * 1.5)
    draw_math(draw, *jit(SOL_X, y, 2), "2x^2 + 5x - 3 = 0", pen, pen_sup, BLUE)
    # Factoring grid (orange): clearly below the equation
    h_y = y + GLYPH_H + HINT_GAP
    draw.text(jit(SOL_X + 22, h_y, 1),                   "2   -1", font=pen_sm, fill=ORANGE)
    draw.text(jit(SOL_X + 22, h_y + SM_H + 4, 1),        "1    3", font=pen_sm, fill=ORANGE)

    y += int(LH * 2.0)   # room for two hint lines
    draw_math(draw, *jit(SOL_X, y, 2), "(2x - 1)(x + 3) = 0", pen, pen_sup, BLUE)

    y += LH
    draw_math(draw, *jit(SOL_X, y, 2), "x = 1/2  or  x = -3", pen, pen_sup, BLUE)

    y += LH
    # Green highlight only on the answer value "b = -3"
    prefix2_w = int(draw.textlength(".. 작은 수  ", font=pen))
    ans2_val_w = pen.getbbox("b = -3")[2]
    img = highlight(img, SOL_X + prefix2_w - 2, y - 1,
                    SOL_X + prefix2_w + ans2_val_w + 6, y + GLYPH_H + 3, HL_GREEN)
    draw = ImageDraw.Draw(img)
    draw_math(draw, *jit(SOL_X, y, 2), ".. 작은 수  b = -3", pen, pen_sup, BLUE)

    # ── Final answer ────────────────────────────────────────────────────────
    y += int(LH * 1.5)
    draw_math(draw, *jit(SOL_X, y, 2), ".. a - b = 2 - (-3) = 5", pen, pen_sup, BLUE)
    # Green checkmark
    ck_x, ck_y = SOL_X - 22, y + int(FS * 0.5)
    draw.line([(ck_x, ck_y), (ck_x + 7, ck_y + 9)],  fill=GREEN, width=2)
    draw.line([(ck_x + 7, ck_y + 9), (ck_x + 19, ck_y - 6)], fill=GREEN, width=2)

    # ── Hand-drawn red circle on ④ 5 ──────────────────────────────────────
    # ④ is at pixel (762, 390)–(804, 413); the "5" follows at ~(793, 391)–(804, 413)
    # Circle the whole "④ 5" area
    hand_circle(draw, cx=797, cy=401, rx=36, ry=17, color=RED, width=2)

    # ── Purple concept box ─────────────────────────────────────────────────
    PAD   = 14
    box_x1 = 750
    box_y1 = y + int(LH * 1.3)
    box_x2 = 1490
    box_y2 = box_y1 + int(FS * 4.8)
    draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline=PURPLE, width=2)

    pen_cb  = ImageFont.truetype(PEN, int(FS * 0.88))
    pen_cbs = ImageFont.truetype(PEN, int(FS * 0.60))

    draw.text(jit(box_x1 + PAD, box_y1 + PAD, 1), "[ 핵심 개념 ]", font=pen_cb, fill=PURPLE)
    draw_math(draw, box_x1 + PAD, box_y1 + PAD + int(FS * 1.3),
              "이차방정식 ax^2 + bx + c = 0 의 인수분해 : 두 수 p, q 로 a(x+p)(x+q) = 0",
              pen_cb, pen_cbs, PURPLE)
    draw_math(draw, box_x1 + PAD, box_y1 + PAD + int(FS * 2.6),
              "두 근의 합 : -b/a,   두 근의 곱 : c/a   (근과 계수의 관계)",
              pen_cb, pen_cbs, PURPLE)

    return img


def main():
    random.seed(42)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return

    inp = pdf_to_image(pdf_path, page_num=0)
    inp.save(OUT_DIR / "input.png")
    print(f"Saved {OUT_DIR / 'input.png'}")

    out = overlay_solution(inp)
    out.save(OUT_DIR / "output.png")
    print(f"Saved {OUT_DIR / 'output.png'}")


if __name__ == "__main__":
    main()
