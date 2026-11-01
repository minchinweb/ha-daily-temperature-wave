# Copyright (c) 2025 William Minchin
"""Config and options flows for Daily Temperature Wave.

Everything is stored in the entry's options (data stays empty), so the
options flow can change any of it, including clearing the solar noon
override.
"""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TimeSelector,
)
import voluptuous as vol

from .constants import (
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_SOLAR_NOON_OVERRIDE,
    CONF_STEP_INTERVAL,
    CONF_STEP_RESOLUTION,
    CONF_WAVE_SPREAD,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_NAME,
    DEFAULT_STEP_INTERVAL,
    DEFAULT_STEP_RESOLUTION,
    DEFAULT_WAVE_SPREAD,
    DOMAIN,
)
from .wave import parse_step, parse_temperature_celsius

WAVE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP): TextSelector(),
        vol.Required(CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP): TextSelector(),
        vol.Required(CONF_WAVE_SPREAD, default=DEFAULT_WAVE_SPREAD): NumberSelector(
            NumberSelectorConfig(
                min=0.2, max=5.0, step=0.1, mode=NumberSelectorMode.BOX
            )
        ),
        vol.Required(
            CONF_STEP_RESOLUTION, default=DEFAULT_STEP_RESOLUTION
        ): TextSelector(),
        vol.Required(CONF_STEP_INTERVAL, default=DEFAULT_STEP_INTERVAL): NumberSelector(
            NumberSelectorConfig(
                min=1,
                max=240,
                step=1,
                unit_of_measurement="min",
                mode=NumberSelectorMode.BOX,
            )
        ),
        vol.Optional(CONF_SOLAR_NOON_OVERRIDE): TimeSelector(),
    }
)

USER_SCHEMA = vol.Schema(
    {vol.Required(CONF_NAME, default=DEFAULT_NAME): TextSelector()}
).extend(WAVE_SCHEMA.schema)


def validate(user_input: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Check the form, and normalize it into options.

    Returns:
        The options to store, and the form errors (empty if it's valid).
    """
    errors: dict[str, str] = {}
    temps = {}
    for key in (CONF_MIN_TEMP, CONF_MAX_TEMP):
        try:
            temps[key] = parse_temperature_celsius(user_input[key])
        except ValueError:
            errors[key] = "invalid_temperature"
    if len(temps) == 2 and temps[CONF_MIN_TEMP] >= temps[CONF_MAX_TEMP]:
        errors["base"] = "min_max_invalid"
    try:
        parse_step(user_input[CONF_STEP_RESOLUTION])
    except ValueError:
        errors[CONF_STEP_RESOLUTION] = "invalid_step"

    options = {
        CONF_MIN_TEMP: user_input[CONF_MIN_TEMP].strip(),
        CONF_MAX_TEMP: user_input[CONF_MAX_TEMP].strip(),
        CONF_WAVE_SPREAD: float(user_input[CONF_WAVE_SPREAD]),
        CONF_STEP_RESOLUTION: user_input[CONF_STEP_RESOLUTION].strip(),
        CONF_STEP_INTERVAL: int(user_input[CONF_STEP_INTERVAL]),
        # stored even when empty, so clearing it in the options flow sticks
        CONF_SOLAR_NOON_OVERRIDE: user_input.get(CONF_SOLAR_NOON_OVERRIDE) or None,
    }
    return options, errors


class DailyTemperatureWaveConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add a Daily Temperature Wave (more than one is fine, e.g. per room)."""

    # Entries from 1.0.0 (settings in `data`) still work: the coordinator
    # merges data and options, and ignores the old `unit_system`.
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for a name and the wave's settings."""
        errors: dict[str, str] = {}
        if user_input is not None:
            options, errors = validate(user_input)
            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME].strip() or DEFAULT_NAME,
                    data={},
                    options=options,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(USER_SCHEMA, user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Change the settings of an existing entry."""
        return DailyTemperatureWaveOptionsFlow()


class DailyTemperatureWaveOptionsFlow(OptionsFlow):
    """Change the wave's settings (the integration reloads afterwards)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the current settings for editing."""
        errors: dict[str, str] = {}
        if user_input is not None:
            options, errors = validate(user_input)
            if not errors:
                return self.async_create_entry(data=options)

        current = user_input or {
            **self.config_entry.data,
            **self.config_entry.options,
        }
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(WAVE_SCHEMA, current),
            errors=errors,
        )
