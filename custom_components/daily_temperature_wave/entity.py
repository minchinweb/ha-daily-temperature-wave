# Copyright (c) 2025 William Minchin
"""Base entity: one device per config entry, fed by the coordinator."""

from __future__ import annotations

from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.unit_conversion import TemperatureConverter

from .constants import DOMAIN
from .coordinator import DailyTemperatureWaveCoordinator


class DailyTemperatureWaveEntity(CoordinatorEntity[DailyTemperatureWaveCoordinator]):
    """Common naming, device and unit handling."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DailyTemperatureWaveCoordinator, key: str) -> None:
        """Name the entity after ``key`` (its translation key)."""
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            entry_type=DeviceEntryType.SERVICE,
        )

    def display_temperature(self, celsius: float) -> float:
        """Convert to the user's unit, for attributes (which HA won't convert)."""
        unit = self.hass.config.units.temperature_unit
        return round(
            TemperatureConverter.convert(celsius, UnitOfTemperature.CELSIUS, unit), 1
        )
