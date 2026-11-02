# Copyright (c) 2025 William Minchin
"""The peak offset moves the wave's peak away from solar noon."""

from __future__ import annotations

from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.daily_temperature_wave.constants import CONF_PEAK_OFFSET


@pytest.fixture
def options(options: dict[str, Any]) -> dict[str, Any]:
    """Solar noon is 13:00 local; peak two hours after it."""
    return {**options, CONF_PEAK_OFFSET: 120}


async def test_peak_offset_moves_the_peak(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    # 15:00 PST is 23:00 UTC: the peak, 30 °C (metric in tests)
    freezer.move_to("2026-01-15 23:00:00+00:00")
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    state = hass.states.get("sensor.daily_temperature_wave_current")
    assert float(state.state) == pytest.approx(30, abs=0.05)
    assert state.attributes["hours_from_noon"] == pytest.approx(0, abs=0.01)
