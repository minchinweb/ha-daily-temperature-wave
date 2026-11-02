# Copyright (c) 2025 William Minchin
"""The chart image entity.

The `hass` fixture is in US/Pacific; the entry fixes solar noon at 13:00.
"""

from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

CHART = "image.daily_temperature_wave_chart"
# 07:10 PST; the chart was last drawn at 07:10
MORNING = "2026-01-15 15:10:00+00:00"


async def _setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def _fetch(hass: HomeAssistant, client: ClientSessionGenerator) -> str:
    """Get the image as a dashboard does, with the entity's access token.

    (`hass_client`'s login token would be rejected: the clock is frozen
    before it was issued.)
    """
    token = hass.states.get(CHART).attributes["access_token"]
    http = await client()
    response = await http.get(f"/api/image_proxy/{CHART}?token={token}")
    assert response.status == HTTPStatus.OK
    assert response.content_type == "image/svg+xml"
    return await response.text()


async def test_chart_image(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    config_entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    freezer.move_to(MORNING)
    await _setup(hass, config_entry)

    state = hass.states.get(CHART)
    assert state.state.startswith("2026-01-15T07:10:00")
    assert len(state.attributes["points"]) == 49  # every 30 minutes, both midnights
    assert state.attributes["points"][0]["datetime"].startswith("2026-01-15T00:00")

    svg = await _fetch(hass, hass_client_no_auth)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "solar noon 13:00" in svg
    assert "30°C" in svg  # the high
    assert "20°C" in svg  # the low


async def test_chart_in_fahrenheit(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    config_entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    hass.config.units = US_CUSTOMARY_SYSTEM
    freezer.move_to(MORNING)
    await _setup(hass, config_entry)

    assert hass.states.get(CHART).attributes["points"][0]["temperature"] > 60
    svg = await _fetch(hass, hass_client_no_auth)
    assert "86°F" in svg
    assert "68°F" in svg


async def test_chart_redraws_every_five_minutes(
    hass: HomeAssistant, config_entry: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(MORNING)
    await _setup(hass, config_entry)
    first = hass.states.get(CHART).state

    async def tick(minutes: int) -> str:
        freezer.tick(timedelta(minutes=minutes))
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
        return hass.states.get(CHART).state

    assert await tick(1) == first  # 07:11
    later = await tick(4)  # 07:15
    assert later != first
    assert later.startswith("2026-01-15T07:15:00")
