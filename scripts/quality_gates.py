"""Stage 1 품질 게이트 측정 스크립트."""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageFont

FONTS_DIR = Path(__file__).parent.parent / "fonts"

# 중등 수학 특수기호 전체 목록
MATH_SYMBOLS = "∴∵≥≤≠√∫∑∏∞∈∉⊂⊃∪∩∧∨¬→←↔±°′″αβγπΩ²³"


def gate_font_coverage() -> bool:
    """Gate: Nanum 폰트로 수학 특수기호 렌더링 가능 확인."""
    print("\n[Gate 1] 폰트 커버리지")
    pen_path = FONTS_DIR / "NanumPenScript-Regular.ttf"
    gothic_path = FONTS_DIR / "NanumGothic-Regular.ttf"

    if not pen_path.exists() or not gothic_path.exists():
        print("  FAIL: 폰트 파일 없음 — python scripts/download_fonts.py 실행")
        return False

    pen_font = ImageFont.truetype(str(pen_path), 32)
    gothic_font = ImageFont.truetype(str(gothic_path), 32)

    img = Image.new("RGB", (800, 100), "white")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), MATH_SYMBOLS, font=gothic_font, fill=(0, 0, 0))
    draw.text((10, 50), "가나다라 x = √2 ∴ y ≠ 0", font=pen_font, fill=(0, 0, 0))
    img.save("quality_gate_font_coverage.png")

    print(f"  OK: 렌더링 완료 → quality_gate_font_coverage.png 확인")
    print(f"  확인 항목: □ 박스 없이 모든 기호가 렌더링됐는지 육안 검사")
    return True


def gate_dpi_rendering() -> bool:
    """Gate: 72/150/300dpi × A4/Letter 8종 조합 렌더링."""
    print("\n[Gate 2] DPI 렌더링")
    from solver.render_overlay import render_overlay
    from solver.models import Annotation, Point, AnnotationStyle

    DPIS = [72, 150, 300]
    SIZES = {"A4": (595, 842), "Letter": (612, 792)}
    TEST_ANN = [
        Annotation("text", "y = (x-1)² - 4", Point(50, 200), "blue", AnnotationStyle(font_size=28)),
        Annotation("box", "이차함수 표준형: y = a(x-p)² + q", Point(50, 680), "purple", AnnotationStyle(font_size=20)),
    ]

    from solver.layout_annotations import layout_annotations
    from solver.models import SolutionData

    solution = SolutionData(
        steps=[], final_answer="x = 1 ± 2", annotations=TEST_ANN,
        confidence=0.85, verified=True
    )

    for dpi in DPIS:
        for name, (w72, h72) in SIZES.items():
            scale = dpi / 72
            img = Image.new("RGB", (int(w72 * scale), int(h72 * scale)), "white")
            anns = layout_annotations(solution, dpi)
            result = render_overlay(img, anns)
            out = f"quality_gate_{dpi}dpi_{name}.png"
            result.save(out)
            print(f"  {dpi}dpi {name}: {out}")

    print("  확인 항목: annotation이 이미지 밖으로 벗어나지 않는지 육안 검사")
    return True


def gate_vision_baseline() -> None:
    """Gate: Vision 정확도 기준선 (수동 측정 안내)."""
    print("\n[Gate 3] Vision 정확도 기준선 (수동 측정)")
    print("  1. 중등 수학 문제 50개 수집 (교과서 캡처 또는 직접 촬영)")
    print("  2. 각 문제에 대해 extract_problem 실행")
    print("  3. 수동으로 OCR 정확도 채점 (수식·한글 모두 올바르면 정답)")
    print("  4. 정확도 < 80%이면:")
    print("     → extract_problem에 interactive=True 파라미터 추가")
    print("     → '이 문제가 맞나요? [y/N]' 프롬프트 구현")
    print("     → pipeline.run(interactive=True) 옵션 추가")


def gate_annotation_position(sample_dir: str | None = None) -> None:
    """Gate: 그래프 문제 10개 annotation 위치 검사."""
    print("\n[Gate 4] Annotation 위치 정확도 (수동 측정)")
    print("  1. 그래프 포함 수학 문제 10개 수집")
    print("  2. 파이프라인 실행 후 출력 이미지 확인")
    print("  3. 합격 기준: annotation bbox가 문제 텍스트 bbox 바깥에 위치")
    print("  4. 미합격 시 generate_solution 프롬프트의 problem_bottom 여백 조정")


if __name__ == "__main__":
    print("=== Stage 1 품질 게이트 ===")
    gate_font_coverage()
    gate_dpi_rendering()
    gate_vision_baseline()
    gate_annotation_position()
    print("\n완료. 생성된 PNG 파일을 육안으로 검사하세요.")
