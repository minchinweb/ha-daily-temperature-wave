"""
Config flow for Daily Temperature Wave integration.
"""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .constants import (
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_SOLAR_NOON_OVERRIDE,
    CONF_STEP_INTERVAL,
    CONF_STEP_RESOLUTION,
    CONF_UNIT_SYSTEM,
    CONF_WAVE_SPREAD,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_STEP_INTERVAL,
    DEFAULT_STEP_RESOLUTION,
    DEFAULT_UNIT_SYSTEM,
    DEFAULT_WAVE_SPREAD,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class DailyTemperatureWaveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Daily Temperature Wave."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._config: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        self._errors = {}

        if user_input is not None:
            # Validate input
            if user_input[CONF_MIN_TEMP] >= user_input[CONF_MAX_TEMP]:
                self._errors["base"] = "min_max_invalid"
            else:
                # Create config entry
                return self.async_create_entry(
                    title="Daily Temperature Wave",
                    data=user_input,
                )

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MIN_TEMP,
                        default=DEFAULT_MIN_TEMP,
                    ): str,
                    vol.Required(
                        CONF_MAX_TEMP,
                        default=DEFAULT_MAX_TEMP,
                    ): str,
                    vol.Required(
                        CONF_WAVE_SPREAD,
                        default=DEFAULT_WAVE_SPREAD,
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=5.0)),
                    vol.Required(
                        CONF_STEP_RESOLUTION,
                        default=DEFAULT_STEP_RESOLUTION,
                    ): str,
                    vol.Required(
                        CONF_STEP_INTERVAL,
                        default=DEFAULT_STEP_INTERVAL,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=120)),
                    vol.Required(
                        CONF_UNIT_SYSTEM,
                        default=DEFAULT_UNIT_SYSTEM,
                    ): vol.In(["metric", "imperial"]),
                    vol.Optional(
                        CONF_SOLAR_NOON_OVERRIDE,
                    ): str,
                }
            ),
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return DailyTemperatureWaveOptionsFlow(config_entry)


class DailyTemperatureWaveOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Daily Temperature Wave."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._options = dict(config_entry.options)
        self._errors: Dict[str, str] = {}

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        self._errors = {}

        if user_input is not None:
            # Validate input
            min_temp_val, min_temp_unit = self._parse_temperature(
                user_input[CONF_MIN_TEMP]
            )
            max_temp_val, max_temp_unit = self._parse_temperature(
                user_input[CONF_MAX_TEMP]
            )

            if min_temp_val >= max_temp_val:
                self._errors["base"] = "min_max_invalid"
            else:
                # Update options
                self._options.update(user_input)
                return self.async_create_entry(
                    title="",
                    data=self._options,
                )

        # Show the options form
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MIN_TEMP,
                        default=self._options.get(CONF_MIN_TEMP, DEFAULT_MIN_TEMP),
                    ): str,
                    vol.Required(
                        CONF_MAX_TEMP,
                        default=self._options.get(CONF_MAX_TEMP, DEFAULT_MAX_TEMP),
                    ): str,
                    vol.Required(
                        CONF_WAVE_SPREAD,
                        default=self._options.get(
                            CONF_WAVE_SPREAD, DEFAULT_WAVE_SPREAD
                        ),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=5.0)),
                    vol.Required(
                        CONF_STEP_RESOLUTION,
                        default=self._options.get(
                            CONF_STEP_RESOLUTION, DEFAULT_STEP_RESOLUTION
                        ),
                    ): str,
                    vol.Required(
                        CONF_STEP_INTERVAL,
                        default=self._options.get(
                            CONF_STEP_INTERVAL, DEFAULT_STEP_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=120)),
                    vol.Required(
                        CONF_UNIT_SYSTEM,
                        default=self._options.get(
                            CONF_UNIT_SYSTEM, DEFAULT_UNIT_SYSTEM
                        ),
                    ): vol.In(["metric", "imperial"]),
                    vol.Optional(
                        CONF_SOLAR_NOON_OVERRIDE,
                        default=self._options.get(CONF_SOLAR_NOON_OVERRIDE, ""),
                    ): str,
                }
            ),
            errors=self._errors,
        )

    def _parse_temperature(self, temp_str: str) -> tuple:
        """Parse temperature string into value and unit."""
        temp_str = temp_str.strip().upper()
        if temp_str.endswith("F"):
            return float(temp_str[:-1]), "F"
        elif temp_str.endswith("C"):
            return float(temp_str[:-1]), "C"
        else:
            return float(temp_str), "C"


@config_entries.HANDLERS.register(DOMAIN)
class FlowHandler:
    """Config flow handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the flow handler."""
        self.config_entry = config_entry

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        return await DailyTemperatureWaveConfigFlow().async_step_user(user_input)

    async def async_step_import(
        self, import_config: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_config)
