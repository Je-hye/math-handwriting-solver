"""Nanum 폰트를 fonts/ 디렉터리에 다운로드한다."""
import urllib.request
from pathlib import Path

FONTS = {
    "NanumPenScript-Regular.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/nanumpenscript/"
        "NanumPenScript-Regular.ttf"
    ),
    "NanumGothic-Regular.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/nanumgothic/"
        "NanumGothic-Regular.ttf"
    ),
}

fonts_dir = Path(__file__).parent.parent / "fonts"
fonts_dir.mkdir(exist_ok=True)

for filename, url in FONTS.items():
    dest = fonts_dir / filename
    if dest.exists():
        print(f"Already exists: {filename}")
        continue
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, dest)
    print(f"Saved: {dest}")
