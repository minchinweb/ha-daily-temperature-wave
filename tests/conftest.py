# Copyright (c) 2025 William Minchin
"""Shared fixtures; most come from pytest-homeassistant-custom-component."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.daily_temperature_wave.constants import (
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_SOLAR_NOON_OVERRIDE,
    CONF_STEP_INTERVAL,
    CONF_STEP_RESOLUTION,
    CONF_WAVE_SPREAD,
    DOMAIN,
)

OPTIONS: dict[str, Any] = {
    CONF_MIN_TEMP: "20C",
    CONF_MAX_TEMP: "30C",
    CONF_WAVE_SPREAD: 1.0,
    CONF_STEP_RESOLUTION: "1F",
    CONF_STEP_INTERVAL: 30,
    # fixed, so the expected temperatures don't depend on the date
    CONF_SOLAR_NOON_OVERRIDE: "13:00:00",
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> Iterator[None]:
    """Let Home Assistant load the integration from `custom_components/`."""
    return


@pytest.fixture
def options() -> dict[str, Any]:
    """The entry's options; override in a test module to change them."""
    return dict(OPTIONS)


@pytest.fixture
def config_entry(options: dict[str, Any]) -> MockConfigEntry:
    """A config entry, as the config flow would create it."""
    return MockConfigEntry(
        domain=DOMAIN, title="Daily Temperature Wave", data={}, options=options
    )
