# Copyright (c) 2025 William Minchin
"""The sensors and binary sensor, set up through a config entry.

The `hass` fixture is in US/Pacific; the entry fixes solar noon at 13:00.
"""

from __future__ import annotations

from datetime import timedelta
from itertools import pairwise

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.daily_temperature_wave.constants import (
    CONF_SOLAR_NOON_OVERRIDE,
)

# 13:00 PST, solar noon
NOON = "2026-01-15 21:00:00+00:00"
# 07:10 PST: 5h50m before noon; the 30-minute step started at 07:00
MORNING = "2026-01-15 15:10:00+00:00"

ENTITIES = [
    "binary_sensor.daily_temperature_wave_rising",
    "sensor.daily_temperature_wave_current",
    "sensor.daily_temperature_wave_current_step",
    "sensor.daily_temperature_wave_forecast_24h",
    "sensor.daily_temperature_wave_forecast_24h_step",
    "sensor.daily_temperature_wave_forecast_7d",
    "sensor.daily_temperature_wave_forecast_7d_step",
    "sensor.daily_temperature_wave_visual",
]


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED


def _temp(hass: HomeAssistant, entity_id: str) -> float:
    return float(hass.states.get(entity_id).state)


async def test_entities_created(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
    freezer: FrozenDateTimeFactory,
) -> None:
    freezer.move_to(NOON)
    await _setup(hass, config_entry)
    for entity_id in ENTITIES:
        entry = entity_registry.async_get(entity_id)
        assert entry is not None, entity_id
        assert entry.unique_id.startswith(config_entry.entry_id)
        assert hass.states.get(entity_id).state not in ("unknown", "unavailable")


async def test_peak_at_solar_noon(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(NOON)
    await _setup(hass, config_entry)

    current = hass.states.get("sensor.daily_temperature_wave_current")
    assert float(current.state) == pytest.approx(30.0)
    assert current.attributes["unit_of_measurement"] == UnitOfTemperature.CELSIUS
    assert current.attributes["device_class"] == "temperature"
    assert current.attributes["hours_from_noon"] == 0
    assert current.attributes["solar_noon"].startswith("2026-01-15T13:00:00")
    assert _temp(hass, "sensor.daily_temperature_wave_current_step") == 30.0
    assert hass.states.get("binary_sensor.daily_temperature_wave_rising").state == "off"


async def test_morning(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(MORNING)
    await _setup(hass, config_entry)

    # a little over the midpoint (25 °C at 07:00)
    assert 25 < _temp(hass, "sensor.daily_temperature_wave_current") < 25.5
    # held at the 07:00 value, 25 °C = 77 °F, already on a 1 °F step
    assert _temp(hass, "sensor.daily_temperature_wave_current_step") == 25.0
    assert hass.states.get("binary_sensor.daily_temperature_wave_rising").state == "on"


async def test_updates_every_minute(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(MORNING)
    await _setup(hass, config_entry)
    before = _temp(hass, "sensor.daily_temperature_wave_current")

    freezer.tick(timedelta(hours=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert _temp(hass, "sensor.daily_temperature_wave_current") > before


async def test_forecasts(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(NOON)
    await _setup(hass, config_entry)

    hourly = hass.states.get("sensor.daily_temperature_wave_forecast_24h")
    forecast = hourly.attributes["forecast"]
    assert len(forecast) == 24
    assert forecast[0]["datetime"].startswith("2026-01-15T13:00:00")
    assert forecast[0]["temperature"] == 30.0
    assert forecast[12]["temperature"] == 20.0  # solar midnight
    # state: the coming hour
    assert float(hourly.state) == pytest.approx(forecast[1]["temperature"], abs=0.05)

    stepped = hass.states.get("sensor.daily_temperature_wave_forecast_24h_step")
    assert len(stepped.attributes["forecast"]) == 48  # every 30 minutes

    daily = hass.states.get("sensor.daily_temperature_wave_forecast_7d")
    days = daily.attributes["forecast"]
    assert len(days) == 7
    assert days[0] == {
        "date": "2026-01-15",
        "solar_noon": "2026-01-15T13:00:00-08:00",
        "high": 30.0,
        "low": 20.0,
    }
    assert float(daily.state) == 30.0


async def test_schedule(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    """Today's change points, midnight to midnight, whatever the time now."""
    freezer.move_to(MORNING)
    await _setup(hass, config_entry)
    schedule = hass.states.get(
        "sensor.daily_temperature_wave_forecast_24h_step"
    ).attributes["schedule"]

    times = [step["time"] for step in schedule]
    temps = [step["temperature"] for step in schedule]
    assert times[0] == "00:00"
    assert times == sorted(times)
    assert all(t[-2:] in ("00", "30") for t in times)  # on the step interval
    assert all(a != b for a, b in pairwise(temps))  # only changes
    # 20-30 °C in 1 °F steps: 68-86 °F, up to noon and back down; where the
    # wave climbs over 1 °F per half hour, some degrees are skipped
    assert (min(temps), max(temps)) == (20.0, 30.0)
    assert 10 < len(set(temps)) <= 19
    assert 13 * 60 >= _minutes(times[temps.index(30.0)]) >= 12 * 60
    assert temps[times.index("07:00")] == 25.0
    assert schedule[0]["datetime"] == "2026-01-15T00:00:00-08:00"


def _minutes(hh_mm: str) -> int:
    hours, minutes = hh_mm.split(":")
    return int(hours) * 60 + int(minutes)


async def test_visual(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(NOON)
    await _setup(hass, config_entry)
    visual = hass.states.get("sensor.daily_temperature_wave_visual")
    assert visual.attributes["svg"].startswith("<svg")
    assert "13:00" in visual.attributes["svg"]
    assert len(visual.attributes["points"]) == 49


async def test_us_customary_units(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    hass.config.units = US_CUSTOMARY_SYSTEM
    freezer.move_to(NOON)
    await _setup(hass, config_entry)

    current = hass.states.get("sensor.daily_temperature_wave_current")
    assert current.attributes["unit_of_measurement"] == UnitOfTemperature.FAHRENHEIT
    assert float(current.state) == pytest.approx(86.0)
    forecast = hass.states.get("sensor.daily_temperature_wave_forecast_7d")
    assert forecast.attributes["forecast"][0]["low"] == 68.0
    stepped = hass.states.get("sensor.daily_temperature_wave_forecast_24h_step")
    schedule = [step["temperature"] for step in stepped.attributes["schedule"]]
    assert schedule == [round(t) for t in schedule]  # whole °F
    assert max(schedule) == 86.0


@pytest.mark.parametrize("options", [{CONF_SOLAR_NOON_OVERRIDE: None}])
async def test_solar_noon_from_location(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    """Without an override, solar noon comes from the configured location."""
    freezer.move_to(NOON)
    await _setup(hass, config_entry)
    noon = hass.states.get("sensor.daily_temperature_wave_current").attributes[
        "solar_noon"
    ]
    # San Diego (the test location) in January: about 11:58 PST
    assert noon.startswith("2026-01-15T11:5")


@pytest.mark.parametrize("options", [{"min_temp": "hot"}])
async def test_bad_options_fail_setup(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.SETUP_ERROR


async def test_unload(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(NOON)
    await _setup(hass, config_entry)
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.NOT_LOADED
