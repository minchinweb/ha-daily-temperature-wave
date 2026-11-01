# Copyright (c) 2025 William Minchin
"""The wave maths and temperature parsing (no Home Assistant instance needed)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from custom_components.daily_temperature_wave.wave import (
    hours_from_noon,
    interval_start,
    is_rising,
    parse_step,
    parse_temperature,
    parse_temperature_celsius,
    round_to_step,
    temperature_at,
    wave_fraction,
)

EDMONTON = ZoneInfo("America/Edmonton")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("20C", (20.0, "C")),
        ("20c", (20.0, "C")),
        (" 68 °F ", (68.0, "F")),
        ("-5.5C", (-5.5, "C")),
        ("21", (21.0, "C")),
        (21, (21.0, "C")),
        (21.5, (21.5, "C")),
    ],
)
def test_parse_temperature(value, expected):
    assert parse_temperature(value) == expected


@pytest.mark.parametrize("value", ["", "warm", "20K", "C", "20CC"])
def test_parse_temperature_rejects(value):
    with pytest.raises(ValueError):
        parse_temperature(value)


def test_parse_temperature_celsius_converts_fahrenheit():
    assert parse_temperature_celsius("68F") == pytest.approx(20.0)
    assert parse_temperature_celsius("212F") == pytest.approx(100.0)


def test_parse_step_keeps_its_unit():
    # a 1 °F *difference*, not -17.2 °C
    assert parse_step("1F") == (1.0, "F")


@pytest.mark.parametrize("value", ["0C", "-1F"])
def test_parse_step_must_be_positive(value):
    with pytest.raises(ValueError):
        parse_step(value)


@pytest.mark.parametrize(
    ("hours", "expected"),
    [(0, 1.0), (6, 0.5), (-6, 0.5), (12, 0.0), (-12, 0.0), (24, 1.0)],
)
def test_wave_fraction_peaks_at_noon(hours, expected):
    assert wave_fraction(hours) == pytest.approx(expected)


@pytest.mark.parametrize("spread", [0.5, 1.0, 2.0, 3.0])
def test_spread_keeps_peak_and_trough(spread):
    assert wave_fraction(0, spread) == pytest.approx(1.0)
    assert wave_fraction(12, spread) == pytest.approx(0.0)
    # still continuous across solar midnight
    assert wave_fraction(11.99, spread) == pytest.approx(wave_fraction(-11.99, spread))


def test_spread_sharpens_the_peak():
    assert wave_fraction(6, 2.0) < wave_fraction(6, 1.0) < wave_fraction(6, 0.5)


def test_temperature_at():
    assert temperature_at(0, 20, 30) == pytest.approx(30)
    assert temperature_at(12, 20, 30) == pytest.approx(20)
    assert temperature_at(-6, 20, 30) == pytest.approx(25)


@pytest.mark.parametrize(
    ("hours", "rising"), [(-11, True), (-0.1, True), (0, False), (6, False)]
)
def test_is_rising(hours, rising):
    assert is_rising(hours) is rising


def test_hours_from_noon_wraps():
    noon = datetime(2026, 1, 15, 13, 0, tzinfo=EDMONTON)
    assert hours_from_noon(noon, noon) == 0
    assert hours_from_noon(noon - timedelta(hours=6), noon) == -6
    assert hours_from_noon(noon + timedelta(hours=13), noon) == -11
    assert hours_from_noon(noon - timedelta(hours=13), noon) == 11


def test_hours_from_noon_mixed_time_zones():
    noon = datetime(2026, 1, 15, 13, 0, tzinfo=EDMONTON)  # 20:00 UTC
    assert hours_from_noon(datetime(2026, 1, 15, 21, 0, tzinfo=UTC), noon) == 1


def test_hours_from_noon_across_dst():
    # 2026-03-08 02:00 MST -> 03:00 MDT; midnight to 13:00 is 12 real hours
    noon = datetime(2026, 3, 8, 13, 0, tzinfo=EDMONTON)
    midnight = datetime(2026, 3, 8, 0, 0, tzinfo=EDMONTON)
    # (wall-clock time would say 13 hours, which wraps to +11)
    assert hours_from_noon(midnight, noon) == -12


@pytest.mark.parametrize(
    ("temp_c", "step", "unit", "expected_c"),
    [
        (22.0, 1, "F", (72 - 32) * 5 / 9),  # 71.6 °F -> 72 °F
        (22.2, 0.5, "C", 22.0),
        (22.3, 0.5, "C", 22.5),
        (30.0, 1, "F", 30.0),  # 86 °F exactly
    ],
)
def test_round_to_step(temp_c, step, unit, expected_c):
    assert round_to_step(temp_c, step, unit) == pytest.approx(expected_c)


@pytest.mark.parametrize(
    ("hour", "minute", "interval", "expected"),
    [
        (7, 10, 30, (7, 0)),
        (7, 30, 30, (7, 30)),
        (7, 59, 30, (7, 30)),
        (7, 59, 45, (7, 30)),
    ],
)
def test_interval_start(hour, minute, interval, expected):
    moment = datetime(2026, 1, 15, hour, minute, 42, tzinfo=EDMONTON)
    start = interval_start(moment, interval)
    assert (start.hour, start.minute, start.second) == (*expected, 0)
    assert start.tzinfo is EDMONTON
