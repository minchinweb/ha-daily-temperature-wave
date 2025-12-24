"""
Basic tests that don't require Home Assistant dependencies.
"""

import os
import sys
import unittest

# Add the custom components to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from daily_temperature_wave.utils.temperature import (
    convert_from_celsius,
    convert_to_celsius,
    get_unit_symbol,
    parse_step_resolution,
    parse_temperature_value,
    round_to_step,
)


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality without Home Assistant dependencies."""

    def test_parse_temperature_value(self):
        """Test parsing temperature values with different formats."""
        # Test Celsius values
        self.assertEqual(parse_temperature_value("20C"), (20.0, "C"))
        self.assertEqual(parse_temperature_value("20c"), (20.0, "C"))
        self.assertEqual(
            parse_temperature_value("20"), (20.0, "C")
        )  # Default to Celsius

        # Test Fahrenheit values
        self.assertEqual(parse_temperature_value("68F"), (68.0, "F"))
        self.assertEqual(parse_temperature_value("68f"), (68.0, "F"))

        # Test numeric values
        self.assertEqual(parse_temperature_value(20), (20.0, "C"))
        self.assertEqual(parse_temperature_value(20.5), (20.5, "C"))

    def test_convert_to_celsius(self):
        """Test conversion to Celsius."""
        # Celsius to Celsius (should be unchanged)
        self.assertEqual(convert_to_celsius(20, "C"), 20)

        # Fahrenheit to Celsius
        self.assertAlmostEqual(convert_to_celsius(68, "F"), 20, places=2)  # 68°F = 20°C
        self.assertAlmostEqual(convert_to_celsius(32, "F"), 0, places=2)  # 32°F = 0°C
        self.assertAlmostEqual(
            convert_to_celsius(212, "F"), 100, places=2
        )  # 212°F = 100°C

    def test_convert_from_celsius(self):
        """Test conversion from Celsius."""
        # Celsius to Celsius (should be unchanged)
        self.assertEqual(convert_from_celsius(20, "C"), 20)

        # Celsius to Fahrenheit
        self.assertAlmostEqual(
            convert_from_celsius(20, "F"), 68, places=2
        )  # 20°C = 68°F
        self.assertAlmostEqual(convert_from_celsius(0, "F"), 32, places=2)  # 0°C = 32°F
        self.assertAlmostEqual(
            convert_from_celsius(100, "F"), 212, places=2
        )  # 100°C = 212°F

    def test_round_to_step(self):
        """Test rounding to step."""
        # Test with step = 1
        self.assertEqual(round_to_step(20.3, 1), 20)
        self.assertEqual(round_to_step(20.6, 1), 21)

        # Test with step = 0.5
        self.assertEqual(round_to_step(20.2, 0.5), 20.0)
        self.assertEqual(round_to_step(20.3, 0.5), 20.5)
        self.assertEqual(round_to_step(20.7, 0.5), 20.5)

        # Test with step = 0 (should return original value)
        self.assertEqual(round_to_step(20.3, 0), 20.3)

    def test_get_unit_symbol(self):
        """Test getting unit symbols."""
        self.assertEqual(get_unit_symbol("C"), "°C")
        self.assertEqual(get_unit_symbol("F"), "°F")
        self.assertEqual(get_unit_symbol("c"), "°C")  # Case insensitive
        self.assertEqual(get_unit_symbol("f"), "°F")  # Case insensitive

    def test_parse_step_resolution(self):
        """Test parsing step resolution."""
        self.assertEqual(parse_step_resolution("1F"), (1.0, "F"))
        self.assertEqual(parse_step_resolution("0.5C"), (0.5, "C"))
        self.assertEqual(parse_step_resolution("1"), (1.0, "C"))  # Default to Celsius

    def test_sine_wave_calculation(self):
        """Test basic sine wave calculation logic."""
        import math

        # Test sine wave at key points
        min_temp = 20
        max_temp = 30
        wave_spread = 1.0

        # At solar noon (0 hours from noon)
        hours_from_noon = 0
        sine_value = math.sin(math.pi * hours_from_noon / (12 * wave_spread))
        temp_normalized = (sine_value + 1) / 2
        temp = min_temp + (max_temp - min_temp) * temp_normalized
        self.assertAlmostEqual(temp, 30, places=1)  # Should be max temp

        # 12 hours from noon (should be min temp)
        hours_from_noon = 12
        sine_value = math.sin(math.pi * hours_from_noon / (12 * wave_spread))
        temp_normalized = (sine_value + 1) / 2
        temp = min_temp + (max_temp - min_temp) * temp_normalized
        self.assertAlmostEqual(temp, 20, places=1)  # Should be min temp

        # 6 hours from noon (should be midpoint)
        hours_from_noon = 6
        sine_value = math.sin(math.pi * hours_from_noon / (12 * wave_spread))
        temp_normalized = (sine_value + 1) / 2
        temp = min_temp + (max_temp - min_temp) * temp_normalized
        self.assertAlmostEqual(temp, 25, places=1)  # Should be midpoint


if __name__ == "__main__":
    unittest.main()
