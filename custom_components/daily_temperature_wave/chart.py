# Copyright (c) 2025 William Minchin
"""An SVG chart of today's wave, served by the chart image entity."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .coordinator import WaveState

WIDTH = 400  # the drawing's own coordinates (the viewBox)
HEIGHT = 200
SCALE = 3  # the image is this many times the drawing's size
LEFT, RIGHT, TOP, BOTTOM = 44, 12, 24, 24  # padding around the plot
RIGHT_WITH_AXIS = 44  # room for a second temperature axis on the right
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


def _labelled_temps(low: float, high: float) -> list[float]:
    """Round temperatures in ``low``..``high``, every nice step (at most ~10)."""
    span = high - low
    step = next((s for s in (1, 2, 5, 10, 20, 50) if span / s <= 10), 50)
    first = math.ceil(low / step) * step
    count = math.floor(high / step) - math.ceil(low / step) + 1
    return [first + i * step for i in range(max(count, 0))]


def render_svg(
    state: WaveState,
    convert: Callable[[float], float],
    unit: str,
    second: tuple[Callable[[float], float], Callable[[float], float], str]
    | None = None,
) -> str:
    """Draw today (midnight to midnight): the wave, its steps, solar noon and now.

    Args:
        state: The coordinator's latest calculation.
        convert: Celsius to the unit to label the chart in.
        unit: That unit's symbol, e.g. ``"°C"``.
        second: For a wave typed in another unit: Celsius to that unit, that
            unit back to Celsius, and its symbol. It gets its own axis on the
            right, so both units show.

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
    right = RIGHT_WITH_AXIS if second else RIGHT
    plot_w, plot_h = WIDTH - LEFT - right, HEIGHT - TOP - BOTTOM

    def x(hour: float) -> float:
        return round(LEFT + plot_w * hour / day_hours, 1)

    def y(temp: float) -> float:
        return round(TOP + plot_h * (high - temp) / span, 1)

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH * SCALE}" '
            f'height="{HEIGHT * SCALE}" viewBox="0 0 {WIDTH} {HEIGHT}">'
        ),
        f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{BACKGROUND}"/>',
    ]

    # hour grid every 3 hours; labels every 6, so they don't crowd
    for hour in range(0, 25, 3):
        hx = x(hour * day_hours / 24)
        parts.append(
            f'<line x1="{hx}" y1="{TOP}" x2="{hx}" y2="{HEIGHT - BOTTOM}" '
            f'stroke="{GRID_COLOR}" stroke-width="0.5"/>'
            # a tick just outside the bottom edge
            f'<line x1="{hx}" y1="{HEIGHT - BOTTOM}" x2="{hx}" '
            f'y2="{HEIGHT - BOTTOM + 4}" '
            f'stroke="{TEXT_COLOR}" stroke-width="0.8"/>'
        )
        if hour % 6 == 0:
            anchor = "end" if hour == 24 else "middle"  # keep 24:00 inside the edge
            parts.append(
                f'<text x="{hx}" y="{HEIGHT - 8}" text-anchor="{anchor}" {FONT} '
                f'fill="{TEXT_COLOR}">{hour:02d}:00</text>'
            )
    # a line at every whole degree, in the unit shown
    for degree in range(math.ceil(low), math.floor(high) + 1):
        dy = y(degree)
        parts.append(
            f'<line x1="{LEFT}" y1="{dy}" x2="{WIDTH - right}" y2="{dy}" '
            f'stroke="{GRID_COLOR}" stroke-width="0.3"/>'
        )
    # a faint line at each change in the schedule (the first is midnight)
    for change in state.schedule[1:]:
        cx = x(_hour_of_day(change.moment, midnight))
        parts.append(
            f'<line x1="{cx}" y1="{TOP}" x2="{cx}" y2="{HEIGHT - BOTTOM}" '
            f'stroke="{GRID_COLOR}" stroke-width="0.3"/>'
        )
    # temperature labels on the left, every nice step, with a tick outside
    for temp in _labelled_temps(low, high):
        ty = y(temp)
        parts.append(
            f'<line x1="{LEFT - 4}" y1="{ty}" x2="{LEFT}" y2="{ty}" '
            f'stroke="{TEXT_COLOR}" stroke-width="0.8"/>'
            f'<text x="{LEFT - 7}" y="{ty + 4}" text-anchor="end" {FONT} '
            f'fill="{TEXT_COLOR}">{temp:g}{unit}</text>'
        )

    # the second axis, on the right, at the same heights
    if second:
        to_second, to_celsius, second_unit = second
        celsius = [p.temperature for p in state.curve] + [
            p.temperature for p in state.schedule
        ]
        for value in _labelled_temps(to_second(min(celsius)), to_second(max(celsius))):
            sy = y(convert(to_celsius(value)))
            parts.append(
                f'<line x1="{WIDTH - right}" y1="{sy}" x2="{WIDTH - right + 4}" '
                f'y2="{sy}" stroke="{TEXT_COLOR}" stroke-width="0.8"/>'
                f'<text x="{WIDTH - right + 7}" y="{sy + 4}" {FONT} '
                f'fill="{TEXT_COLOR}">{value:g}{second_unit}</text>'
            )

    # solar noon
    noon_x = x(_hour_of_day(state.solar_noon, midnight))
    parts.append(
        f'<line x1="{noon_x}" y1="{TOP}" x2="{noon_x}" y2="{HEIGHT - BOTTOM}" '
        f'stroke="{GRID_COLOR}" stroke-dasharray="4,4"/>'
        f'<text x="{noon_x}" y="{TOP - 8}" text-anchor="middle" {FONT} '
        f'fill="{TEXT_COLOR}">solar noon {state.solar_noon:%H:%M}</text>'
    )

    # the peak, when the peak offset moves it away from solar noon
    if state.peak != state.solar_noon:
        peak_x = x(_hour_of_day(state.peak, midnight))
        parts.append(
            f'<line x1="{peak_x}" y1="{TOP}" x2="{peak_x}" y2="{HEIGHT - BOTTOM}" '
            f'stroke="{CURVE_COLOR}" stroke-dasharray="2,3"/>'
            f'<text x="{peak_x + 4}" y="{HEIGHT - BOTTOM - 6}" {FONT} '
            f'fill="{CURVE_COLOR}">peak {state.peak:%H:%M}</text>'
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
        f'<line x1="{now_x}" y1="{TOP}" x2="{now_x}" y2="{HEIGHT - BOTTOM}" '
        f'stroke="{NOW_COLOR}" stroke-width="0.8" opacity="0.6"/>'
        f'<circle cx="{now_x}" cy="{now_y}" r="4" fill="{NOW_COLOR}"/>'
        f'<text x="{label_x}" y="{max(now_y - 8, TOP + 10)}" text-anchor="{anchor}" '
        f'{FONT} fill="{NOW_COLOR}">{now_temp:.1f}{unit}</text>'
    )

    parts.append("</svg>")
    return "".join(parts)
