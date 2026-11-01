# Copyright (c) 2025 William Minchin
"""The config and options flows."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
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

USER_INPUT = {
    "name": "Living room",
    CONF_MIN_TEMP: " 68F ",
    CONF_MAX_TEMP: "22C",
    CONF_WAVE_SPREAD: 1.5,
    CONF_STEP_RESOLUTION: "1F",
    CONF_STEP_INTERVAL: 30.0,  # NumberSelector gives floats
}


async def _start(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}
    return result


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living room"
    assert result["data"] == {}
    assert result["options"] == {
        CONF_MIN_TEMP: "68F",
        CONF_MAX_TEMP: "22C",
        CONF_WAVE_SPREAD: 1.5,
        CONF_STEP_RESOLUTION: "1F",
        CONF_STEP_INTERVAL: 30,
        CONF_SOLAR_NOON_OVERRIDE: None,
    }
    await hass.async_block_till_done()
    assert hass.states.get("sensor.living_room_current") is not None


async def test_user_flow_min_must_be_below_max(hass: HomeAssistant) -> None:
    result = await _start(hass)
    # compared in Celsius: 80 °F is 26.7 °C, above the 25 °C maximum
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_MIN_TEMP: "80F", CONF_MAX_TEMP: "25"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "min_max_invalid"}


async def test_user_flow_invalid_values(hass: HomeAssistant) -> None:
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {**USER_INPUT, CONF_MIN_TEMP: "chilly", CONF_STEP_RESOLUTION: "0F"},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {
        CONF_MIN_TEMP: "invalid_temperature",
        CONF_STEP_RESOLUTION: "invalid_step",
    }

    # and it recovers once fixed
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_options_flow_updates_and_clears_override(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.options[CONF_SOLAR_NOON_OVERRIDE] == "13:00:00"

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    new_input = {
        CONF_MIN_TEMP: "18C",
        CONF_MAX_TEMP: "24C",
        CONF_WAVE_SPREAD: 1.0,
        CONF_STEP_RESOLUTION: "0.5C",
        CONF_STEP_INTERVAL: 15,
        # override left empty
    }
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], new_input
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert config_entry.options[CONF_MAX_TEMP] == "24C"
    assert config_entry.options[CONF_SOLAR_NOON_OVERRIDE] is None
    # reloaded with the new settings
    assert config_entry.runtime_data.settings.max_temp == 24
    assert config_entry.runtime_data.settings.solar_noon_override is None


async def test_options_flow_validates(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_MIN_TEMP: "30C",
            CONF_MAX_TEMP: "20C",
            CONF_WAVE_SPREAD: 1.0,
            CONF_STEP_RESOLUTION: "1F",
            CONF_STEP_INTERVAL: 30,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "min_max_invalid"}
