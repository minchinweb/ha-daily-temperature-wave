# Copyright (c) 2026 MinchinWeb
"""Outline the Daily Temperature Wave wordmark in the logo masters.

The wordmark in ``brand/logo.svg`` and ``brand/dark_logo.svg`` is a path, not
live text, so the logos need no font installed. This script redraws that path
from the bundled Figtree font (weight 600) and trims the viewBox to the text.
The cap height is 0.40 of the logo height, the same as the set's other logos.
The icon is not touched.

Run from the repository root::

    uv run --with fonttools python scripts/outline_wordmark.py
"""

from __future__ import annotations

import math
from pathlib import Path
import re

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "brand"
FONT = BRAND / "fonts" / "Figtree-Variable.ttf"
WORDMARK = "Daily Temperature Wave"
WEIGHT = 600
# The logo is 229 units tall. Its cap height is 40% of that.
LOGO_HEIGHT = 229.0
CAP_RATIO = 0.40
ORIGIN_X = 263.5
MID_Y = 114.5


def _outline(
    font, size: float, origin: float = ORIGIN_X
) -> tuple[str, tuple[float, float, float, float]]:
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    scale = size / font["head"].unitsPerEm
    baseline = MID_Y + font["OS/2"].sCapHeight * scale / 2
    path = SVGPathPen(glyphs, ntos=lambda value: f"{value:.2f}")
    bounds = BoundsPen(glyphs)
    x = origin
    for char in WORDMARK:
        name = cmap[ord(char)]
        transform = (scale, 0, 0, -scale, x, baseline)
        glyphs[name].draw(TransformPen(path, transform))
        glyphs[name].draw(TransformPen(bounds, transform))
        x += hmtx[name][0] * scale
    return path.getCommands(), bounds.bounds


def main() -> None:
    font = instantiateVariableFont(TTFont(FONT), {"wght": WEIGHT})
    size = CAP_RATIO * LOGO_HEIGHT / (font["OS/2"].sCapHeight / font["head"].unitsPerEm)
    commands, (_, _, right, _) = _outline(font, size)
    width = math.ceil(right)
    for name in ("logo.svg", "dark_logo.svg"):
        path = BRAND / name
        text = path.read_text(encoding="utf-8")
        fill = re.search(r'<path id="[^"]*" fill="([^"]+)" d="', text).group(1)
        text = re.sub(
            r'viewBox="0 0 \d+ 229"', f'viewBox="0 0 {width} 229"', text, count=1
        )
        text = re.sub(
            r'<path id="[^"]*" fill="[^"]+" d="[^"]*"/>',
            lambda _, fill=fill: f'<path id="wordmark" fill="{fill}" d="{commands}"/>',
            text,
            count=1,
        )
        path.write_text(text, encoding="utf-8", newline="")
        print(f"{name}: viewBox width {width}, font size {size:.2f}")


if __name__ == "__main__":
    main()
