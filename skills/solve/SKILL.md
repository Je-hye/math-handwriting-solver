# /solve — Math Problem Solver

Solve a handwritten or printed math problem from an image or PDF. Renders a handwriting-style solution overlay on the original image.

## Educational Basis

This skill's output format is designed based on cognitive science research:

| Principle | Design decision | Source |
|-----------|----------------|--------|
| Worked Example Effect | All intermediate steps shown explicitly | Barbieri et al. (2023) meta-analysis |
| Split-Attention Effect | Annotations placed adjacent to their formulas | ZDM Springer (2022) |
| Strategic Color Coding | 5-color scheme for different annotation types | arXiv 2411.14605 |
| Concept Box Effect | Purple box mandatory in every solution | NWEA Mapping Math (2024) |

## Prerequisites Check

Before running, verify in this order:

**1. Installation**
```bash
python -m solver --help
```
If this fails: `pip install -e .` in the repo root.

**2. API key**
```bash
echo $ANTHROPIC_API_KEY
```
If empty: `export ANTHROPIC_API_KEY=<your-api-key>`

**3. File exists** — confirm the path is valid.

**4. Format** — only `jpg`, `jpeg`, `png`, `pdf` supported.

## Usage

```bash
python -m solver "<filepath>"
```

Output is saved as `{stem}_solved{ext}` in the same directory.

## Confidence Levels

| Confidence | Meaning | What to tell the user |
|------------|---------|----------------------|
| ≥ 0.85 | sympy verification passed | Show output path, no warning |
| 0.80 – 0.85 | Borderline | "풀이를 확인해보는 것을 권장합니다" |
| < 0.80 | Low confidence | "AI 풀이를 반드시 확인하세요. 선생님께 검토를 받으세요" |

## Error Handling

| Error | Cause | Response |
|-------|-------|----------|
| `ModuleNotFoundError: solver` | Not installed | `pip install -e .` in repo root |
| `FileNotFoundError: .../fonts/` | Font file missing | "fonts/ 디렉터리를 확인하세요. repo에 번들되어 있어야 합니다" |
| `ANTHROPIC_API_KEY` | API key missing | `export ANTHROPIC_API_KEY=<your-api-key>` |
| `Unsupported format` | Wrong file type | jpg, png, pdf만 지원 |
| `File not found` | Wrong path | 절대 경로로 재시도 |

## After Showing the Solution

Always include this message after a successful solve:

> "이 풀이를 한 번 읽은 후, 책을 덮고 혼자 다시 풀어보세요. 직접 풀어보는 것이 이해를 확인하는 가장 좋은 방법입니다."

This is based on the Worked Example Fading principle: viewing a complete solution is most effective when followed by independent practice (Atkinson et al., 2000).

## Annotation Color Scheme

| Color | Purpose |
|-------|---------|
| blue | Calculation steps, formula transformations |
| red | Emphasis, circles |
| green | Answer checkmark |
| orange | Coordinate and numeric labels |
| purple | Key concept box (always last) |

## Installation

```bash
mkdir -p ~/.claude/skills/solve
cp skills/solve/SKILL.md ~/.claude/skills/solve/SKILL.md
```
