# Copyright (c) 2025 William Minchin
"""A small SVG chart of today's wave, for the visual sensor's ``svg`` attribute."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .coordinator import WaveState

WIDTH = 300
HEIGHT = 150
PADDING = 20
CURVE_COLOR = "#3498db"
NOW_COLOR = "#e74c3c"
GRID_COLOR = "#7f8c8d"
TEXT_COLOR = "#2c3e50"


def _hour_of_day(moment: datetime, midnight: datetime) -> float:
    return (moment.timestamp() - midnight.timestamp()) / 3600


def render_svg(state: WaveState, convert: Callable[[float], float], unit: str) -> str:
    """Draw today's curve (midnight to midnight), solar noon, and now.

    Args:
        state: The coordinator's latest calculation.
        convert: Celsius to the unit to label the chart in.
        unit: That unit's symbol, e.g. ``"°C"``.

    Returns:
        A standalone SVG document.
    """
    midnight = state.curve[0].moment
    temps = [convert(p.temperature) for p in state.curve]
    low, high = min(temps), max(temps)
    span = (high - low) or 1.0
    plot_w, plot_h = WIDTH - 2 * PADDING, HEIGHT - 2 * PADDING

    def x(hour: float) -> float:
        return round(PADDING + plot_w * hour / 24, 1)

    def y(temp: float) -> float:
        return round(PADDING + plot_h * (high - temp) / span, 1)

    path = " ".join(
        f"{'M' if i == 0 else 'L'}{x(_hour_of_day(p.moment, midnight))},{y(t)}"
        for i, (p, t) in enumerate(zip(state.curve, temps, strict=True))
    )
    noon_x = x(_hour_of_day(state.solar_noon, midnight))
    now_x = x(_hour_of_day(state.now, midnight))
    now_temp = convert(state.current)
    now_y = y(now_temp)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
        f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">'
        f'<line x1="{noon_x}" y1="{PADDING}" x2="{noon_x}" '
        f'y2="{HEIGHT - PADDING}" stroke="{GRID_COLOR}" stroke-dasharray="4,4"/>'
        f'<text x="{noon_x}" y="{HEIGHT - 5}" text-anchor="middle" '
        f'font-size="10" fill="{GRID_COLOR}">'
        f"{state.solar_noon:%H:%M}</text>"
        f'<path d="{path}" stroke="{CURVE_COLOR}" stroke-width="2" fill="none"/>'
        f'<circle cx="{now_x}" cy="{now_y}" r="4" fill="{NOW_COLOR}"/>'
        f'<text x="{now_x}" y="{max(now_y - 8, 10)}" text-anchor="middle" '
        f'font-size="11" fill="{NOW_COLOR}">{now_temp:.1f}{unit}</text>'
        f'<text x="2" y="{PADDING + 4}" font-size="10" fill="{TEXT_COLOR}">'
        f"{high:.1f}{unit}</text>"
        f'<text x="2" y="{HEIGHT - PADDING}" font-size="10" fill="{TEXT_COLOR}">'
        f"{low:.1f}{unit}</text>"
        "</svg>"
    )
