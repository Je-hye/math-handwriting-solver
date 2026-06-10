import sys
from pathlib import Path
from .pipeline import run


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python -m solver <filepath>")
        print("  Supported: .jpg .jpeg .png .pdf")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    print(f"Processing: {filepath}")
    output, confidence = run(filepath)
    print(f"Solved: {output}")

    if confidence < 0.8:
        print(
            f"⚠️  Confidence: {confidence:.0%} — AI 풀이를 반드시 확인하세요"
        )


if __name__ == "__main__":
    main()
