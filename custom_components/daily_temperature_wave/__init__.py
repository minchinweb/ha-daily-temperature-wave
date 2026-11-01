# Copyright (c) 2025 William Minchin
"""Daily Temperature Wave: a target temperature that follows the sun.

Sets up one coordinator per config entry; the sensor and binary sensor
platforms read from it.
"""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError

from .constants import PLATFORMS
from .coordinator import (
    DailyTemperatureWaveConfigEntry,
    DailyTemperatureWaveCoordinator,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: DailyTemperatureWaveConfigEntry
) -> bool:
    """Set up Daily Temperature Wave from a config entry."""
    try:
        coordinator = DailyTemperatureWaveCoordinator(hass, entry)
    except ValueError as err:
        # the config flow validates, so only a hand-edited entry gets here
        raise ConfigEntryError(f"Invalid configuration: {err}") from err

    await coordinator.async_config_entry_first_refresh()
    coordinator.async_start()
    entry.runtime_data = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: DailyTemperatureWaveConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_options_updated(
    hass: HomeAssistant, entry: DailyTemperatureWaveConfigEntry
) -> None:
    """Reload, so new options take effect."""
    _LOGGER.debug("Options changed for %s; reloading", entry.title)
    await hass.config_entries.async_reload(entry.entry_id)
