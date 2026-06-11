from __future__ import annotations


def strip_md_json(text: str) -> str:
    """Claude API 응답에서 ```json ... ``` 마크다운 블록을 제거한다."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()
