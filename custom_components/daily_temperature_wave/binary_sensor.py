# Copyright (c) 2025 William Minchin
"""Binary sensors: is the wave rising or falling, smooth and stepped?"""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .constants import (
    BINARY_SENSOR_FALLING,
    BINARY_SENSOR_FALLING_STEP,
    BINARY_SENSOR_RISING,
    BINARY_SENSOR_RISING_STEP,
)
from .coordinator import (
    DailyTemperatureWaveConfigEntry,
    DailyTemperatureWaveCoordinator,
    WaveState,
)
from .entity import DailyTemperatureWaveEntity

PARALLEL_UPDATES = 0

# (key, whether it is on for a given state)
BINARY_SENSORS: tuple[tuple[str, Callable[[WaveState], bool]], ...] = (
    (BINARY_SENSOR_RISING, lambda s: s.rising),
    (BINARY_SENSOR_FALLING, lambda s: s.falling),
    (BINARY_SENSOR_RISING_STEP, lambda s: s.rising_step),
    (BINARY_SENSOR_FALLING_STEP, lambda s: s.falling_step),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DailyTemperatureWaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the binary sensors for a config entry."""
    async_add_entities(
        [
            DailyTemperatureWaveBinarySensor(entry.runtime_data, key, is_on)
            for key, is_on in BINARY_SENSORS
        ]
    )


class DailyTemperatureWaveBinarySensor(DailyTemperatureWaveEntity, BinarySensorEntity):
    """A direction of the wave: on while the temperature is moving that way."""

    def __init__(
        self,
        coordinator: DailyTemperatureWaveCoordinator,
        key: str,
        is_on: Callable[[WaveState], bool],
    ) -> None:
        """Name the sensor after ``key``; ``is_on`` reads its state."""
        super().__init__(coordinator, key)
        self._is_on = is_on

    @property
    def is_on(self) -> bool:
        """Whether the sensor is on."""
        return self._is_on(self.coordinator.data)
