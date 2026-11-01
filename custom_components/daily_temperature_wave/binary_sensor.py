# Copyright (c) 2025 William Minchin
"""Binary sensor: is the wave rising (morning) or falling (afternoon)?"""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .constants import BINARY_SENSOR_RISING
from .coordinator import DailyTemperatureWaveConfigEntry
from .entity import DailyTemperatureWaveEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DailyTemperatureWaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the binary sensor for a config entry."""
    async_add_entities(
        [DailyTemperatureWaveRising(entry.runtime_data, BINARY_SENSOR_RISING)]
    )


class DailyTemperatureWaveRising(DailyTemperatureWaveEntity, BinarySensorEntity):
    """On from solar midnight to solar noon, while the temperature rises."""

    @property
    def is_on(self) -> bool:
        """Whether the temperature is rising."""
        return self.coordinator.data.rising
