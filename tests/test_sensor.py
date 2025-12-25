"""
Unit tests for the Daily Temperature Wave sensors.
"""

import json
import unittest
from datetime import datetime, time
from unittest.mock import MagicMock, patch

from custom_components.daily_temperature_wave.constants import (
    SENSOR_CURRENT,
    SENSOR_CURRENT_STEP,
    SENSOR_FORECAST_7D,
    SENSOR_FORECAST_24H,
    SENSOR_VISUAL,
)
from custom_components.daily_temperature_wave.sensor import (
    SENSOR_DESCRIPTIONS,
    DailyTemperatureWaveSensor,
)


class TestDailyTemperatureWaveSensor(unittest.TestCase):
    """Test Daily Temperature Wave sensor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config entry
        self.mock_config_entry = MagicMock()
        self.mock_config_entry.entry_id = "test_entry"
        self.mock_config_entry.data = {
            "min_temp": "20C",
            "max_temp": "30C",
            "wave_spread": 1.0,
            "step_resolution": "1F",
            "step_interval": 30,
            "unit_system": "metric",
            "solar_noon_override": None,
        }
        self.mock_config_entry.options = {}

    def test_sensor_descriptions(self):
        """Test that all sensor descriptions are defined."""
        self.assertEqual(len(SENSOR_DESCRIPTIONS), 7)

        # Check that all expected sensors are present
        sensor_keys = [desc.key for desc in SENSOR_DESCRIPTIONS]
        self.assertIn(SENSOR_CURRENT, sensor_keys)
        self.assertIn(SENSOR_CURRENT_STEP, sensor_keys)
        self.assertIn(SENSOR_FORECAST_24H, sensor_keys)
        self.assertIn(SENSOR_FORECAST_7D, sensor_keys)
        self.assertIn(SENSOR_VISUAL, sensor_keys)

    def test_sensor_initialization(self):
        """Test sensor initialization."""
        # Test current temperature sensor
        current_sensor = DailyTemperatureWaveSensor(
            self.mock_config_entry, SENSOR_DESCRIPTIONS[0]  # SENSOR_CURRENT
        )

        self.assertEqual(current_sensor._attr_name, "Daily Temperature Wave Current")
        self.assertEqual(current_sensor._attr_unique_id, "test_entry_current")
        self.assertEqual(current_sensor._min_temp_c, 20.0)
        self.assertEqual(current_sensor._max_temp_c, 30.0)
        self.assertEqual(current_sensor._wave_spread, 1.0)
        self.assertEqual(current_sensor._unit_system, "metric")

    @patch("custom_components.daily_temperature_wave.sensor.get_solar_noon")
    @patch("custom_components.daily_temperature_wave.sensor.get_current_solar_position")
    def test_current_temperature_calculation(
        self, mock_solar_position, mock_solar_noon
    ):
        """Test current temperature calculation."""
        # Mock solar noon and position
        mock_solar_noon.return_value = time(12, 0)
        mock_solar_position.return_value = 0.0  # At solar noon

        # Create sensor
        sensor = DailyTemperatureWaveSensor(
            self.mock_config_entry, SENSOR_DESCRIPTIONS[0]  # SENSOR_CURRENT
        )

        # Mock hass
        sensor.hass = MagicMock()

        # Calculate temperature (should be max temp at solar noon)
        temp = sensor._calculate_current_temperature(sensor.hass, time(12, 0))

        # Should be close to max temp (30°C)
        self.assertAlmostEqual(temp, 30.0, places=1)

    @patch("custom_components.daily_temperature_wave.sensor.get_solar_noon")
    @patch("custom_components.daily_temperature_wave.sensor.get_current_solar_position")
    def test_forecast_generation(self, mock_solar_position, mock_solar_noon):
        """Test forecast generation."""
        # Mock solar noon and position
        mock_solar_noon.return_value = time(12, 0)
        mock_solar_position.return_value = 0.0

        # Create 24h forecast sensor
        sensor = DailyTemperatureWaveSensor(
            self.mock_config_entry, SENSOR_DESCRIPTIONS[2]  # SENSOR_FORECAST_24H
        )

        # Mock hass
        sensor.hass = MagicMock()
        sensor.hass.config.time_zone = None

        # Generate forecast
        forecast = sensor._generate_24h_forecast(sensor.hass, time(12, 0))

        # Check forecast structure
        self.assertEqual(len(forecast), 24)

        # Check first forecast item structure
        first_item = forecast[0]
        self.assertIn("time", first_item)
        self.assertIn("temperature", first_item)
        self.assertIn("hours_from_noon", first_item)

    def test_visual_data_generation(self):
        """Test visual data generation."""
        # Create visual sensor
        sensor = DailyTemperatureWaveSensor(
            self.mock_config_entry, SENSOR_DESCRIPTIONS[6]  # SENSOR_VISUAL
        )

        # Mock hass and solar noon
        sensor.hass = MagicMock()
        sensor.hass.config.time_zone = None

        # Generate visual data
        visual_data = sensor._generate_visual_data(sensor.hass, time(12, 0))

        # Check visual data structure
        self.assertIn("points", visual_data)
        self.assertIn("current_position", visual_data)
        self.assertIn("solar_noon", visual_data)
        self.assertIn("temperature_range", visual_data)

        # Check points
        points = visual_data["points"]
        self.assertEqual(len(points), 25)  # 25 points for 24 hours

        # Check current position
        current_pos = visual_data["current_position"]
        self.assertIn("x", current_pos)
        self.assertIn("y", current_pos)
        self.assertIn("temp", current_pos)
        self.assertIn("hours_from_noon", current_pos)


if __name__ == "__main__":
    unittest.main()
