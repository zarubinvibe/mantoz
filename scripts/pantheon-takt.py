#!/usr/bin/env python3
"""Carve the workflow labels onto the blank marble plates of the takt frame.

The takt frame is one generated image with five blank plates. The words on those
plates differ per README language, and an image model cannot be trusted to write
Cyrillic or Chinese correctly, so the text is composited here instead: the same
plates, the same geometry, three deterministic outputs.

    python3 scripts/pantheon-takt.py

Reads the plate rectangles from .github/pantheon/takt-plity.json and the labels
from the stages of .github/pantheon.json, writes docs/assets/pantheon/takt-<lang>.png.

Needs Pillow. It is a build tool for the project's own assets, not a runtime
dependency: `python3 -m pip install pillow` before running it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs/assets/pantheon/takt.png"
PLATES = ROOT / ".github/pantheon/takt-plity.json"
MANIFEST = ROOT / ".github/pantheon.json"

FONTS = {
    "en": "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "ru": "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "zh": "/System/Library/Fonts/Supplemental/Songti.ttc",
}
CARVED = (62, 58, 54)      # charcoal of the palette
HIGHLIGHT = (255, 253, 248)  # the lit lower edge of a real groove


def fit(text: str, font_path: str, box_w: int, box_h: int) -> ImageFont.FreeTypeFont:
    """Largest size that still leaves a margin inside the plate."""
    size = box_h
    while size > 8:
        font = ImageFont.truetype(font_path, size)
        left, top, right, bottom = font.getbbox(text)
        if right - left <= box_w * 0.78 and bottom - top <= box_h * 0.42:
            return font
        size -= 2
    return ImageFont.truetype(font_path, 10)


def carve(language: str, labels: list[str], plates: list[dict]) -> Path:
    image = Image.open(SOURCE).convert("RGB")
    draw = ImageDraw.Draw(image)
    # One size for the whole row. Fitting each plate on its own makes the short
    # words huge and the long ones tiny, and the row stops reading as one frame.
    size = min(fit(label, FONTS[language], plate["w"], plate["h"]).size
               for label, plate in zip(labels, plates))
    shared = ImageFont.truetype(FONTS[language], size)
    for label, plate in zip(labels, plates):
        font = shared
        left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
        x = plate["x"] + (plate["w"] - (right - left)) / 2 - left
        y = plate["y"] + (plate["h"] - (bottom - top)) / 2 - top
        # A groove reads as a dark cut with one lit edge just below it.
        draw.text((x + 1, y + 1), label, font=font, fill=HIGHLIGHT)
        draw.text((x, y), label, font=font, fill=CARVED)
    out = ROOT / f"docs/assets/pantheon/takt-{language}.png"
    image.save(out)
    return out


def main() -> int:
    for path in (SOURCE, PLATES, MANIFEST):
        if not path.is_file():
            print(f"missing: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
    plates = json.loads(PLATES.read_text(encoding="utf-8"))
    stages = json.loads(MANIFEST.read_text(encoding="utf-8"))["visuals"]["stages"]
    if len(plates) != len(stages):
        print(f"{len(plates)} plates but {len(stages)} stages", file=sys.stderr)
        return 1
    for language in FONTS:
        labels = [stage[f"diagram_{language}"] for stage in stages]
        print("written", carve(language, labels, plates).relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
