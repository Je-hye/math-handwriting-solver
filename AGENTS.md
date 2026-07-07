# Math Handwriting Solver — Agent Usage Guide

This file provides instructions for AI agents (Claude Code, Gemini CLI, OpenAI Codex, etc.) on how to use the math-handwriting-solver tool.

## When to Use

When a user asks to solve a math problem from an image or PDF file.

## Prerequisites Check

Before invoking the solver, check in this order:

1. **Installation check**
   ```bash
   python -m solver --help
   ```
   If this fails → tell the user to run `pip install -e .` in the repo root.

2. **API key check**
   ```bash
   echo $ANTHROPIC_API_KEY
   ```
   If empty → tell the user: `export ANTHROPIC_API_KEY=<your-api-key>`

3. **File existence check** — confirm the input file path exists before proceeding.

4. **Format check** — only `jpg`, `jpeg`, `png`, `pdf` are supported.

## Invocation

```bash
python -m solver "<filepath>"
```

Example:
```bash
python -m solver problem.jpg
python -m solver ~/Downloads/exam.pdf
```

Output file is saved as `{stem}_solved{ext}` in the same directory as the input.

## Output Interpretation

| Output | Meaning | What to tell the user |
|--------|---------|----------------------|
| `Solved: <path>` | Success | Show the output path |
| `confidence ≥ 0.85` | sympy-verified | No warning needed |
| `confidence 0.80–0.85` | Borderline | "풀이를 확인해보는 것을 권장합니다" |
| `confidence < 0.80` | Low | "AI 풀이를 반드시 확인하세요. 선생님께 검토를 받으세요" |

After showing the solution, always include:
> "이 풀이를 한 번 읽은 후, 책을 덮고 혼자 다시 풀어보세요."

## Error Handling

| Error | Cause | Tell the user |
|-------|-------|---------------|
| `ModuleNotFoundError: solver` | Not installed | `pip install -e .` in repo root |
| `FileNotFoundError: .../fonts/` | Missing font files | Check `fonts/` directory in repo |
| `ANTHROPIC_API_KEY` related | Missing API key | `export ANTHROPIC_API_KEY=<your-api-key>` |
| `Unsupported format` | Wrong file type | Only jpg/png/pdf supported |
| `File not found` | Wrong path | Ask user to verify path, try absolute path |

## For Claude Code Users

See `skills/solve/SKILL.md` for the `/solve` skill which provides enhanced guidance including educational research basis and step-by-step prerequisites.
