# Copyright (c) 2025 William Minchin
"""An SVG chart of today's wave, served by the chart image entity."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .coordinator import WaveState

WIDTH = 400
HEIGHT = 200
LEFT, RIGHT, TOP, BOTTOM = 44, 12, 24, 24  # padding around the plot
# a light card of its own, so the chart reads the same on light and dark themes
BACKGROUND = "#ffffff"
CURVE_COLOR = "#3498db"
STEP_COLOR = "#9b59b6"
NOW_COLOR = "#e74c3c"
GRID_COLOR = "#bdc3c7"
TEXT_COLOR = "#2c3e50"
FONT = 'font-family="sans-serif" font-size="11"'


def _hour_of_day(moment: datetime, midnight: datetime) -> float:
    return (moment.timestamp() - midnight.timestamp()) / 3600


def render_svg(state: WaveState, convert: Callable[[float], float], unit: str) -> str:
    """Draw today (midnight to midnight): the wave, its steps, solar noon and now.

    Args:
        state: The coordinator's latest calculation.
        convert: Celsius to the unit to label the chart in.
        unit: That unit's symbol, e.g. ``"°C"``.

    Returns:
        A standalone SVG document.
    """
    midnight = state.curve[0].moment
    day_hours = _hour_of_day(state.curve[-1].moment, midnight)  # 23-25 with DST
    temps = [convert(p.temperature) for p in state.curve]
    steps = [(p.moment, convert(p.temperature)) for p in state.schedule]
    low = min(*temps, *(t for _, t in steps))
    high = max(*temps, *(t for _, t in steps))
    span = (high - low) or 1.0
    plot_w, plot_h = WIDTH - LEFT - RIGHT, HEIGHT - TOP - BOTTOM

    def x(hour: float) -> float:
        return round(LEFT + plot_w * hour / day_hours, 1)

    def y(temp: float) -> float:
        return round(TOP + plot_h * (high - temp) / span, 1)

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
            f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">'
        ),
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{BACKGROUND}"/>',
    ]

    # hour grid and labels, every 6 hours
    for hour in range(0, 25, 6):
        hx = x(hour * day_hours / 24)
        anchor = "end" if hour == 24 else "middle"  # keep 24:00 inside the edge
        parts.append(
            f'<line x1="{hx}" y1="{TOP}" x2="{hx}" y2="{HEIGHT - BOTTOM}" '
            f'stroke="{GRID_COLOR}" stroke-width="0.5"/>'
            f'<text x="{hx}" y="{HEIGHT - 8}" text-anchor="{anchor}" {FONT} '
            f'fill="{TEXT_COLOR}">{hour:02d}:00</text>'
        )
    # temperature labels: high and low
    for temp in (high, low):
        parts.append(
            f'<text x="{LEFT - 4}" y="{y(temp) + 4}" text-anchor="end" {FONT} '
            f'fill="{TEXT_COLOR}">{temp:.1f}{unit}</text>'
        )

    # solar noon
    noon_x = x(_hour_of_day(state.solar_noon, midnight))
    parts.append(
        f'<line x1="{noon_x}" y1="{TOP}" x2="{noon_x}" y2="{HEIGHT - BOTTOM}" '
        f'stroke="{GRID_COLOR}" stroke-dasharray="4,4"/>'
        f'<text x="{noon_x}" y="{TOP - 8}" text-anchor="middle" {FONT} '
        f'fill="{TEXT_COLOR}">solar noon {state.solar_noon:%H:%M}</text>'
    )

    # the stepped schedule, held to the end of the day
    if steps:
        (first, first_temp), *rest = steps
        path = f"M{x(_hour_of_day(first, midnight))},{y(first_temp)}"
        for moment, temp in rest:
            # across to the change, then up or down to the new temperature
            path += f"H{x(_hour_of_day(moment, midnight))}V{y(temp)}"
        path += f"H{x(day_hours)}"
        parts.append(
            f'<path d="{path}" stroke="{STEP_COLOR}" stroke-width="1.2" '
            f'stroke-dasharray="4,3" fill="none"/>'
        )

    # the wave
    curve = " ".join(
        f"{'M' if i == 0 else 'L'}{x(_hour_of_day(p.moment, midnight))},{y(t)}"
        for i, (p, t) in enumerate(zip(state.curve, temps, strict=True))
    )
    parts.append(
        f'<path d="{curve}" stroke="{CURVE_COLOR}" stroke-width="2" fill="none"/>'
    )

    # now
    now_x = x(_hour_of_day(state.now, midnight))
    now_temp = convert(state.current)
    now_y = y(now_temp)
    anchor = "end" if now_x > WIDTH - 60 else "start"
    label_x = now_x - 6 if anchor == "end" else now_x + 6
    parts.append(
        f'<circle cx="{now_x}" cy="{now_y}" r="4" fill="{NOW_COLOR}"/>'
        f'<text x="{label_x}" y="{max(now_y - 8, TOP + 10)}" text-anchor="{anchor}" '
        f'{FONT} fill="{NOW_COLOR}">{now_temp:.1f}{unit}</text>'
    )

    parts.append("</svg>")
    return "".join(parts)
