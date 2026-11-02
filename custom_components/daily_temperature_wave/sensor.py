# Copyright (c) 2025 William Minchin
"""Temperature sensors: the current wave value and its forecasts.

Each sensor's state is a temperature (in Celsius, which Home Assistant
converts to the user's unit). Forecasts are attributes, in the user's unit,
and are not recorded in history.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .constants import (
    SENSOR_CURRENT,
    SENSOR_CURRENT_STEP,
    SENSOR_FORECAST_7D,
    SENSOR_FORECAST_7D_STEP,
    SENSOR_FORECAST_24H,
    SENSOR_FORECAST_24H_STEP,
)
from .coordinator import (
    DailyForecast,
    DailyTemperatureWaveConfigEntry,
    DailyTemperatureWaveCoordinator,
    TimedTemperature,
    WaveState,
)
from .entity import DailyTemperatureWaveEntity

# the coordinator updates every entity at once; no polling
PARALLEL_UPDATES = 0

type Convert = Callable[[float], float]


@dataclass(frozen=True, kw_only=True)
class WaveSensorEntityDescription(SensorEntityDescription):
    """How to get one sensor's state and attributes from a `WaveState`."""

    value_fn: Callable[[WaveState], float]
    attributes_fn: Callable[[WaveState, Convert, str], dict[str, Any]] | None = None


def _timed(points: list[TimedTemperature], convert: Convert) -> list[dict[str, Any]]:
    return [
        {"datetime": p.moment.isoformat(), "temperature": convert(p.temperature)}
        for p in points
    ]


def _schedule(points: list[TimedTemperature], convert: Convert) -> list[dict[str, Any]]:
    return [
        {
            "datetime": p.moment.isoformat(),
            "time": p.moment.strftime("%H:%M"),
            "temperature": convert(p.temperature),
        }
        for p in points
    ]


def _stepped_attributes(state: WaveState, convert: Convert, unit: str) -> dict:
    return {
        "forecast": _timed(state.stepped, convert),
        "schedule": _schedule(state.schedule, convert),
    }


def _daily(days: list[DailyForecast], convert: Convert) -> list[dict[str, Any]]:
    return [
        {
            "date": d.day.isoformat(),
            "solar_noon": d.solar_noon.isoformat(),
            "high": convert(d.high),
            "low": convert(d.low),
        }
        for d in days
    ]


def _current_attributes(state: WaveState, convert: Convert, unit: str) -> dict:
    return {
        "solar_noon": state.solar_noon.isoformat(),
        "hours_from_noon": round(state.hours_from_noon, 2),
        "rising": state.rising,
    }


_TEMPERATURE = {
    "device_class": SensorDeviceClass.TEMPERATURE,
    "native_unit_of_measurement": UnitOfTemperature.CELSIUS,
    "suggested_display_precision": 1,
}

SENSORS: tuple[WaveSensorEntityDescription, ...] = (
    WaveSensorEntityDescription(
        key=SENSOR_CURRENT,
        translation_key=SENSOR_CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.current,
        attributes_fn=_current_attributes,
        **_TEMPERATURE,
    ),
    WaveSensorEntityDescription(
        key=SENSOR_CURRENT_STEP,
        translation_key=SENSOR_CURRENT_STEP,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda s: s.current_step,
        **_TEMPERATURE,
    ),
    # Forecast states: the next entry (the coming hour or step, today's high)
    WaveSensorEntityDescription(
        key=SENSOR_FORECAST_24H,
        translation_key=SENSOR_FORECAST_24H,
        value_fn=lambda s: s.hourly[1].temperature,
        attributes_fn=lambda s, c, u: {"forecast": _timed(s.hourly, c)},
        **_TEMPERATURE,
    ),
    WaveSensorEntityDescription(
        key=SENSOR_FORECAST_24H_STEP,
        translation_key=SENSOR_FORECAST_24H_STEP,
        value_fn=lambda s: s.stepped[1].temperature,
        attributes_fn=_stepped_attributes,
        **_TEMPERATURE,
    ),
    WaveSensorEntityDescription(
        key=SENSOR_FORECAST_7D,
        translation_key=SENSOR_FORECAST_7D,
        value_fn=lambda s: s.daily[0].high,
        attributes_fn=lambda s, c, u: {"forecast": _daily(s.daily, c)},
        **_TEMPERATURE,
    ),
    WaveSensorEntityDescription(
        key=SENSOR_FORECAST_7D_STEP,
        translation_key=SENSOR_FORECAST_7D_STEP,
        value_fn=lambda s: s.daily_step[0].high,
        attributes_fn=lambda s, c, u: {"forecast": _daily(s.daily_step, c)},
        **_TEMPERATURE,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DailyTemperatureWaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the sensors for a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        DailyTemperatureWaveSensor(coordinator, description) for description in SENSORS
    )


class DailyTemperatureWaveSensor(DailyTemperatureWaveEntity, SensorEntity):
    """A temperature read off the wave."""

    entity_description: WaveSensorEntityDescription
    # Forecasts change every minute; keep them out of history.
    _unrecorded_attributes = frozenset({"forecast", "schedule"})

    def __init__(
        self,
        coordinator: DailyTemperatureWaveCoordinator,
        description: WaveSensorEntityDescription,
    ) -> None:
        """Set up the sensor described by ``description``."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float:
        """The temperature, in Celsius."""
        return round(self.entity_description.value_fn(self.coordinator.data), 2)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Forecasts and the like, in the user's unit."""
        attributes_fn = self.entity_description.attributes_fn
        if attributes_fn is None:
            return None
        unit = self.hass.config.units.temperature_unit
        return attributes_fn(self.coordinator.data, self.display_temperature, unit)
