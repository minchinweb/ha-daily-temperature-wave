# Copyright (c) 2025 William Minchin
"""The daily temperature wave itself, and temperature parsing.

Pure functions with no Home Assistant imports, so they can be tested on their
own. All temperatures are in degrees Celsius unless a name says otherwise.

The wave is a raised cosine with a 24-hour period, peaking at solar noon and
bottoming out at solar midnight (12 hours later). ``spread`` reshapes it
without moving those points: 1.0 is a pure cosine, larger values give a
narrower, sharper warm peak (and a longer cool spell), smaller values a
broader one.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
import math
import re

HOURS_PER_DAY = 24
HALF_DAY = HOURS_PER_DAY / 2

CELSIUS = "C"
FAHRENHEIT = "F"

_TEMPERATURE_RE = re.compile(
    r"^\s*(?P<value>[-+]?\d+(?:\.\d+)?)\s*°?\s*(?P<unit>[CF])?\s*$", re.IGNORECASE
)


def parse_temperature(value: str | float) -> tuple[float, str]:
    """Split a temperature such as ``"20C"`` or ``"68 °F"`` into value and unit.

    Args:
        value: The temperature. A number, or a string without a unit, is
            taken as Celsius.

    Returns:
        The number and its unit, ``"C"`` or ``"F"``.

    Raises:
        ValueError: If ``value`` isn't a temperature.
    """
    if isinstance(value, int | float):
        return float(value), CELSIUS
    match = _TEMPERATURE_RE.match(str(value))
    if match is None:
        raise ValueError(f"not a temperature: {value!r}")
    unit = (match["unit"] or CELSIUS).upper()
    return float(match["value"]), unit


def to_celsius(value: float, unit: str) -> float:
    """Convert a temperature in ``unit`` (``"C"`` or ``"F"``) to Celsius."""
    if unit.upper() == FAHRENHEIT:
        return (value - 32) * 5 / 9
    return value


def from_celsius(value: float, unit: str) -> float:
    """Convert a Celsius temperature to ``unit`` (``"C"`` or ``"F"``)."""
    if unit.upper() == FAHRENHEIT:
        return value * 9 / 5 + 32
    return value


def parse_temperature_celsius(value: str | float) -> float:
    """Parse a temperature (see `parse_temperature`) and return it in Celsius."""
    return to_celsius(*parse_temperature(value))


def parse_step(value: str | float) -> tuple[float, str]:
    """Parse a step size such as ``"1F"`` or ``"0.5C"``.

    A step is a temperature *difference*, so it is kept in its own unit rather
    than converted (1 °F of difference is 5/9 °C, not -17.2 °C).

    Raises:
        ValueError: If ``value`` isn't a positive temperature.
    """
    size, unit = parse_temperature(value)
    if size <= 0:
        raise ValueError(f"step must be positive: {value!r}")
    return size, unit


def hours_from_noon(moment: datetime, solar_noon: datetime) -> float:
    """Hours from solar noon to ``moment``, wrapped into [-12, 12).

    Negative values are the morning (temperature rising), positive the
    afternoon and evening (falling).
    """
    # timestamps, so the difference is real elapsed time even across a DST
    # change (subtracting datetimes that share a `tzinfo` uses wall time)
    hours = (moment.timestamp() - solar_noon.timestamp()) / 3600
    return (hours + HALF_DAY) % HOURS_PER_DAY - HALF_DAY


def wave_fraction(hours: float, spread: float = 1.0) -> float:
    """Position on the wave: 1.0 at solar noon, 0.0 at solar midnight.

    Args:
        hours: Hours from solar noon (any value; the wave repeats daily).
        spread: Peak sharpness; 1.0 is a pure cosine.
    """
    raised_cosine = (1 + math.cos(math.pi * hours / HALF_DAY)) / 2
    return raised_cosine**spread


def temperature_at(
    hours: float, min_temp: float, max_temp: float, spread: float = 1.0
) -> float:
    """Temperature ``hours`` from solar noon, between ``min_temp`` and ``max_temp``."""
    return min_temp + (max_temp - min_temp) * wave_fraction(hours, spread)


def is_rising(hours: float) -> bool:
    """Whether the temperature is rising, ``hours`` from solar noon.

    It rises from solar midnight to solar noon, whatever the spread.
    """
    return hours < 0


def round_to_step(temp_c: float, step: float, step_unit: str) -> float:
    """Round a Celsius temperature to the nearest ``step`` in ``step_unit``.

    E.g. with a 1 °F step, 22.0 °C (71.6 °F) becomes 72 °F, returned as
    22.22 °C.
    """
    in_unit = from_celsius(temp_c, step_unit)
    return to_celsius(round(in_unit / step) * step, step_unit)


def interval_start(moment: datetime, minutes: int) -> datetime:
    """Start of the ``minutes``-long interval containing ``moment``.

    Intervals are counted from midnight (in ``moment``'s time zone), so a
    30-minute interval changes on the hour and the half hour, like a
    thermostat schedule.
    """
    midnight = datetime.combine(moment.date(), time(), tzinfo=moment.tzinfo)
    elapsed = (moment - midnight).total_seconds() // 60
    return midnight + timedelta(minutes=elapsed - elapsed % minutes)
