from __future__ import annotations
import base64
import io
import json
import anthropic
from PIL import Image
from .models import ProblemData, BoundingBox, Figure

_SYSTEM = "수학 문제 이미지를 분석해 JSON으로만 응답하는 어시스턴트."

_USER_TEMPLATE = """\
이미지에서 수학 문제를 분석하세요. 아래 JSON 형식으로만 응답하세요 — 다른 텍스트 없이:

{{
  "text": "문제 텍스트 (수식·한글 포함)",
  "problem_type": "equation|graph|geometry|statistics 중 하나",
  "figures": [
    {{"type": "graph|geometry|table", "bbox": {{"x": 0, "y": 0, "width": 100, "height": 100}}}}
  ],
  "bbox": {{"x": 0, "y": 0, "width": 595, "height": 200}}
}}

모든 좌표는 72dpi 기준 픽셀입니다. figures가 없으면 빈 배열을 반환하세요.
이미지 크기 (72dpi 기준): {width}×{height}px
"""


def extract_problem(
    image: Image.Image,
    dpi: int,
    client: anthropic.Anthropic | None = None,
) -> ProblemData:
    if client is None:
        client = anthropic.Anthropic()

    # 72dpi 기준으로 축소 (Vision API 입력 비용 절감)
    if dpi != 72:
        scale = 72 / dpi
        display = image.resize(
            (int(image.width * scale), int(image.height * scale)),
            Image.LANCZOS,
        )
    else:
        display = image

    w72, h72 = display.width, display.height

    buf = io.BytesIO()
    display.save(buf, format="JPEG", quality=85)
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img_b64,
                    },
                },
                {
                    "type": "text",
                    "text": _USER_TEMPLATE.format(width=w72, height=h72),
                },
            ],
        }],
    )

    data = json.loads(response.content[0].text)

    figures = [
        Figure(type=f["type"], bbox=BoundingBox(**f["bbox"]))
        for f in data.get("figures", [])
    ]

    orig_buf = io.BytesIO()
    image.save(orig_buf, format="JPEG", quality=95)

    return ProblemData(
        text=data["text"],
        problem_type=data["problem_type"],
        figures=figures,
        bbox=BoundingBox(**data["bbox"]),
        raw_image=orig_buf.getvalue(),
        image_width=w72,
        image_height=h72,
    )
