"""
Sensor platform for the Daily Temperature Wave component.
"""

import json
import logging
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    DOMAIN,
    ICON_CURRENT,
    ICON_FORECAST,
    ICON_VISUAL,
    SCAN_INTERVAL,
    SENSOR_CURRENT,
    SENSOR_CURRENT_STEP,
    SENSOR_FORECAST_7D,
    SENSOR_FORECAST_7D_STEP,
    SENSOR_FORECAST_24H,
    SENSOR_FORECAST_24H_STEP,
    SENSOR_VISUAL,
)
from .utils.solar import (
    get_current_solar_position,
    get_solar_noon,
    is_temperature_rising,
)
from .utils.temperature import (
    convert_from_celsius,
    convert_to_celsius,
    get_unit_symbol,
    parse_step_resolution,
    parse_temperature_value,
    round_to_step,
)

_LOGGER = logging.getLogger(__name__)


# Sensor descriptions
SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key=SENSOR_CURRENT,
        name="Daily Temperature Wave Current",
        icon=ICON_CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SENSOR_CURRENT_STEP,
        name="Daily Temperature Wave Current (Step)",
        icon=ICON_CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SENSOR_FORECAST_24H,
        name="Daily Temperature Wave Forecast 24h",
        icon=ICON_FORECAST,
        state_class=None,
    ),
    SensorEntityDescription(
        key=SENSOR_FORECAST_24H_STEP,
        name="Daily Temperature Wave Forecast 24h (Step)",
        icon=ICON_FORECAST,
        state_class=None,
    ),
    SensorEntityDescription(
        key=SENSOR_FORECAST_7D,
        name="Daily Temperature Wave Forecast 7d",
        icon=ICON_FORECAST,
        state_class=None,
    ),
    SensorEntityDescription(
        key=SENSOR_FORECAST_7D_STEP,
        name="Daily Temperature Wave Forecast 7d (Step)",
        icon=ICON_FORECAST,
        state_class=None,
    ),
    SensorEntityDescription(
        key=SENSOR_VISUAL,
        name="Daily Temperature Wave Visual",
        icon=ICON_VISUAL,
        state_class=None,
    ),
]


class DailyTemperatureWaveSensor(SensorEntity):
    """Representation of a Daily Temperature Wave sensor."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.config_entry = config_entry
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_icon = description.icon
        self._attr_state_class = description.state_class

        # Get configuration
        self._config = config_entry.data
        self._options = config_entry.options

        # Parse temperature values
        self._min_temp_c, self._min_temp_unit = parse_temperature_value(
            self._config.get("min_temp", "20C")
        )
        self._max_temp_c, self._max_temp_unit = parse_temperature_value(
            self._config.get("max_temp", "30C")
        )

        # Parse step resolution
        self._step_resolution, self._step_unit = parse_step_resolution(
            self._config.get("step_resolution", "1F")
        )
        self._step_interval = self._config.get("step_interval", 30)

        # Get wave spread
        self._wave_spread = self._config.get("wave_spread", 1.0)

        # Get unit system
        self._unit_system = self._config.get("unit_system", "metric")

        # Get solar noon override
        self._solar_noon_override = self._config.get("solar_noon_override")

        # Set unit of measurement
        self._attr_native_unit_of_measurement = get_unit_symbol(
            self._unit_system.upper() if self._unit_system else "C"
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    async def async_update(self) -> None:
        """Update the sensor state."""
        # This will be handled by the async_update method below
        pass

    async def async_update(self) -> None:
        """Update the sensor state."""
        hass = self.hass

        # Get solar noon
        solar_noon = get_solar_noon(hass, self._solar_noon_override)

        # Calculate current temperature based on sensor type
        if self.entity_description.key == SENSOR_CURRENT:
            current_temp = self._calculate_current_temperature(hass, solar_noon)
            self._attr_native_value = current_temp

        elif self.entity_description.key == SENSOR_CURRENT_STEP:
            current_temp = self._calculate_current_temperature(
                hass, solar_noon, stepwise=True
            )
            self._attr_native_value = current_temp

        elif self.entity_description.key == SENSOR_FORECAST_24H:
            forecast = self._generate_24h_forecast(hass, solar_noon)
            self._attr_native_value = json.dumps(forecast)

        elif self.entity_description.key == SENSOR_FORECAST_24H_STEP:
            forecast = self._generate_24h_forecast(hass, solar_noon, stepwise=True)
            self._attr_native_value = json.dumps(forecast)

        elif self.entity_description.key == SENSOR_FORECAST_7D:
            forecast = self._generate_7d_forecast(hass, solar_noon)
            self._attr_native_value = json.dumps(forecast)

        elif self.entity_description.key == SENSOR_FORECAST_7D_STEP:
            forecast = self._generate_7d_forecast(hass, solar_noon, stepwise=True)
            self._attr_native_value = json.dumps(forecast)

        elif self.entity_description.key == SENSOR_VISUAL:
            visual_data = self._generate_visual_data(hass, solar_noon)
            self._attr_native_value = json.dumps(visual_data)

    def _calculate_current_temperature(
        self, hass: HomeAssistant, solar_noon: datetime.time, stepwise: bool = False
    ) -> float:
        """Calculate the current temperature based on sine wave."""
        # Get current position in solar day
        hours_from_noon = get_current_solar_position(hass, solar_noon)

        # Calculate sine wave value
        # Modified sine wave with wave spread
        sine_value = math.sin(math.pi * hours_from_noon / (12 * self._wave_spread))

        # Convert to temperature range (0-1)
        temp_normalized = (sine_value + 1) / 2

        # Calculate temperature in Celsius
        current_temp_c = (
            self._min_temp_c + (self._max_temp_c - self._min_temp_c) * temp_normalized
        )

        # Apply stepwise rounding if needed
        if stepwise:
            # Convert step resolution to Celsius for calculation
            step_c = convert_to_celsius(self._step_resolution, self._step_unit)
            current_temp_c = round_to_step(current_temp_c, step_c)

        # Convert to display units
        return convert_from_celsius(current_temp_c, self._unit_system)

    def _generate_24h_forecast(
        self, hass: HomeAssistant, solar_noon: datetime.time, stepwise: bool = False
    ) -> List[Dict[str, Any]]:
        """Generate 24-hour forecast."""
        forecast = []
        now = datetime.now(hass.config.time_zone)

        for hour in range(24):
            # Calculate time for this hour
            forecast_time = now + timedelta(hours=hour)

            # Calculate hours from solar noon for this time
            current_time = forecast_time.time()
            current_hours = current_time.hour + current_time.minute / 60
            solar_noon_hours = solar_noon.hour + solar_noon.minute / 60
            hours_from_noon = current_hours - solar_noon_hours

            # Normalize to -12 to +12 range
            if hours_from_noon > 12:
                hours_from_noon -= 24
            elif hours_from_noon < -12:
                hours_from_noon += 24

            # Calculate temperature
            sine_value = math.sin(math.pi * hours_from_noon / (12 * self._wave_spread))
            temp_normalized = (sine_value + 1) / 2
            temp_c = (
                self._min_temp_c
                + (self._max_temp_c - self._min_temp_c) * temp_normalized
            )

            # Apply stepwise rounding if needed
            if stepwise:
                step_c = convert_to_celsius(self._step_resolution, self._step_unit)
                temp_c = round_to_step(temp_c, step_c)

            # Convert to display units
            temp_display = convert_from_celsius(temp_c, self._unit_system)

            forecast.append(
                {
                    "time": forecast_time.isoformat(),
                    "temperature": round(temp_display, 1),
                    "hours_from_noon": round(hours_from_noon, 2),
                }
            )

        return forecast

    def _generate_7d_forecast(
        self, hass: HomeAssistant, solar_noon: datetime.time, stepwise: bool = False
    ) -> List[Dict[str, Any]]:
        """Generate 7-day forecast."""
        forecast = []
        now = datetime.now(hass.config.time_zone)

        for day in range(7):
            # Calculate date for this day
            forecast_date = now + timedelta(days=day)

            # For daily forecast, we calculate min and max for the day
            # Min occurs at solar_noon + 12 hours (midnight)
            # Max occurs at solar noon

            # Calculate min temperature (12 hours after solar noon)
            sine_value_min = math.sin(math.pi * 12 / (12 * self._wave_spread))
            temp_normalized_min = (sine_value_min + 1) / 2
            temp_c_min = (
                self._min_temp_c
                + (self._max_temp_c - self._min_temp_c) * temp_normalized_min
            )

            # Calculate max temperature (at solar noon)
            sine_value_max = math.sin(0)  # sin(0) = 0
            temp_normalized_max = (sine_value_max + 1) / 2
            temp_c_max = (
                self._min_temp_c
                + (self._max_temp_c - self._min_temp_c) * temp_normalized_max
            )

            # Apply stepwise rounding if needed
            if stepwise:
                step_c = convert_to_celsius(self._step_resolution, self._step_unit)
                temp_c_min = round_to_step(temp_c_min, step_c)
                temp_c_max = round_to_step(temp_c_max, step_c)

            # Convert to display units
            temp_min_display = convert_from_celsius(temp_c_min, self._unit_system)
            temp_max_display = convert_from_celsius(temp_c_max, self._unit_system)

            forecast.append(
                {
                    "date": forecast_date.strftime("%Y-%m-%d"),
                    "min": round(temp_min_display, 1),
                    "max": round(temp_max_display, 1),
                    "day_of_week": forecast_date.strftime("%A"),
                }
            )

        return forecast

    def _generate_visual_data(
        self, hass: HomeAssistant, solar_noon: datetime.time
    ) -> Dict[str, Any]:
        """Generate visualization data for the temperature curve."""
        # Calculate points for the sine wave
        points = []
        for hour in range(25):  # 25 points for smooth curve (0-24 hours)
            hours_from_noon = hour - 12  # -12 to +12

            sine_value = math.sin(math.pi * hours_from_noon / (12 * self._wave_spread))
            temp_normalized = (sine_value + 1) / 2
            temp_c = (
                self._min_temp_c
                + (self._max_temp_c - self._min_temp_c) * temp_normalized
            )
            temp_display = convert_from_celsius(temp_c, self._unit_system)

            # Scale for visualization (0-100 range)
            x = hour * 10  # 10 pixels per hour
            y = 100 - (temp_display - self._min_temp_c) * 100 / (
                self._max_temp_c - self._min_temp_c
            )

            points.append({"x": x, "y": y, "temp": round(temp_display, 1)})

        # Get current position
        current_hours_from_noon = get_current_solar_position(hass, solar_noon)
        current_temp = self._calculate_current_temperature(hass, solar_noon)

        # Scale current position for visualization
        current_x = (current_hours_from_noon + 12) * 10
        current_y = 100 - (current_temp - self._min_temp_c) * 100 / (
            self._max_temp_c - self._min_temp_c
        )

        return {
            "points": points,
            "current_position": {
                "x": current_x,
                "y": current_y,
                "temp": round(current_temp, 1),
                "hours_from_noon": round(current_hours_from_noon, 1),
            },
            "solar_noon": {
                "hour": solar_noon.hour,
                "minute": solar_noon.minute,
            },
            "temperature_range": {
                "min": self._min_temp_c,
                "max": self._max_temp_c,
                "unit": self._unit_system,
            },
        }


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Daily Temperature Wave sensors."""
    _LOGGER.debug("Setting up Daily Temperature Wave sensors")

    # Create sensors
    sensors = [
        DailyTemperatureWaveSensor(config_entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(sensors, True)


class DailyTemperatureWaveBinarySensor(SensorEntity):
    """Representation of a Daily Temperature Wave binary sensor."""

    def __init__(
        self,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        self.config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_rising"
        self._attr_name = "Daily Temperature Wave Rising"
        self._attr_icon = "mdi:arrow-up" if self._is_rising else "mdi:arrow-down"

        # Get configuration
        self._config = config_entry.data
        self._solar_noon_override = self._config.get("solar_noon_override")
        self._wave_spread = self._config.get("wave_spread", 1.0)

    @property
    def is_on(self) -> bool:
        """Return true if temperature is rising."""
        return self._is_rising

    @property
    def _is_rising(self) -> bool:
        """Check if temperature is currently rising."""
        hass = self.hass
        solar_noon = get_solar_noon(hass, self._solar_noon_override)
        return is_temperature_rising(hass, solar_noon, self._wave_spread)

    async def async_update(self) -> None:
        """Update the binary sensor state."""
        self._is_rising = self._is_rising
        self._attr_icon = "mdi:arrow-up" if self._is_rising else "mdi:arrow-down"
        self.async_write_ha_state()


async def async_setup_binary_sensor_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Daily Temperature Wave binary sensor."""
    _LOGGER.debug("Setting up Daily Temperature Wave binary sensor")

    # Create binary sensor
    binary_sensor = DailyTemperatureWaveBinarySensor(config_entry)

    async_add_entities([binary_sensor], True)
