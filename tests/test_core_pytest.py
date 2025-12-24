"""
Core functionality tests converted to pytest.
"""

import math

import pytest


def parse_temperature_value(value):
    """Parse temperature values with optional unit suffixes."""
    if isinstance(value, (int, float)):
        return float(value), "C"  # Default to Celsius

    if not isinstance(value, str):
        raise ValueError(f"Invalid temperature value: {value}")

    # Handle string inputs like "20C" or "68F"
    value_str = value.strip().upper()

    if value_str.endswith("F"):
        return float(value_str[:-1]), "F"
    elif value_str.endswith("C"):
        return float(value_str[:-1]), "C"
    else:
        # No unit specified, default to Celsius
        return float(value_str), "C"


def convert_to_celsius(value, unit):
    """Convert temperature to Celsius."""
    if unit.upper() == "F":
        return (value - 32) * 5 / 9
    return value


def convert_from_celsius(value, target_unit):
    """Convert temperature from Celsius to target unit."""
    if target_unit.upper() == "F":
        return value * 9 / 5 + 32
    return value


def round_to_step(value, step):
    """Round temperature value to nearest step."""
    if step <= 0:
        return value
    return round(value / step) * step


def calculate_sine_wave_temp(min_temp, max_temp, hours_from_noon, wave_spread=1.0):
    """Calculate temperature using sine wave formula."""
    sine_value = math.sin(math.pi * hours_from_noon / (12 * wave_spread))
    temp_normalized = (sine_value + 1) / 2
    return min_temp + (max_temp - min_temp) * temp_normalized


class TestCoreFunctionality:
    """Test core functionality without any dependencies."""

    def test_parse_temperature_value(self):
        """Test parsing temperature values with different formats."""
        # Test Celsius values
        assert parse_temperature_value("20C") == (20.0, "C")
        assert parse_temperature_value("20c") == (20.0, "C")
        assert parse_temperature_value("20") == (20.0, "C")  # Default to Celsius

        # Test Fahrenheit values
        assert parse_temperature_value("68F") == (68.0, "F")
        assert parse_temperature_value("68f") == (68.0, "F")

        # Test numeric values
        assert parse_temperature_value(20) == (20.0, "C")
        assert parse_temperature_value(20.5) == (20.5, "C")

    def test_convert_to_celsius(self):
        """Test conversion to Celsius."""
        # Celsius to Celsius (should be unchanged)
        assert convert_to_celsius(20, "C") == 20

        # Fahrenheit to Celsius
        assert abs(convert_to_celsius(68, "F") - 20) < 0.01  # 68°F = 20°C
        assert abs(convert_to_celsius(32, "F") - 0) < 0.01  # 32°F = 0°C
        assert abs(convert_to_celsius(212, "F") - 100) < 0.01  # 212°F = 100°C

    def test_convert_from_celsius(self):
        """Test conversion from Celsius."""
        # Celsius to Celsius (should be unchanged)
        assert convert_from_celsius(20, "C") == 20

        # Celsius to Fahrenheit
        assert abs(convert_from_celsius(20, "F") - 68) < 0.01  # 20°C = 68°F
        assert abs(convert_from_celsius(0, "F") - 32) < 0.01  # 0°C = 32°F
        assert abs(convert_from_celsius(100, "F") - 212) < 0.01  # 100°C = 212°F

    def test_round_to_step(self):
        """Test rounding to step."""
        # Test with step = 1
        assert round_to_step(20.3, 1) == 20
        assert round_to_step(20.6, 1) == 21

        # Test with step = 0.5
        assert round_to_step(20.2, 0.5) == 20.0
        assert round_to_step(20.3, 0.5) == 20.5
        assert round_to_step(20.7, 0.5) == 20.5

        # Test with step = 0 (should return original value)
        assert round_to_step(20.3, 0) == 20.3

    def test_sine_wave_calculation(self):
        """Test basic sine wave calculation logic."""
        min_temp = 20
        max_temp = 30
        wave_spread = 1.0

        # At solar noon (0 hours from noon) - sin(0) = 0, so (0+1)/2 = 0.5, should be midpoint
        hours_from_noon = 0
        temp = calculate_sine_wave_temp(
            min_temp, max_temp, hours_from_noon, wave_spread
        )
        assert abs(temp - 25) < 0.1  # Should be midpoint

        # 6 hours before noon (-6) - sin(-π/2) = -1, so (-1+1)/2 = 0, should be min temp
        hours_from_noon = -6
        temp = calculate_sine_wave_temp(
            min_temp, max_temp, hours_from_noon, wave_spread
        )
        assert abs(temp - 20) < 0.1  # Should be min temp

        # 6 hours after noon (+6) - sin(π/2) = 1, so (1+1)/2 = 1, should be max temp
        hours_from_noon = 6
        temp = calculate_sine_wave_temp(
            min_temp, max_temp, hours_from_noon, wave_spread
        )
        assert abs(temp - 30) < 0.1  # Should be max temp

    def test_wave_spread_effect(self):
        """Test how wave spread affects the temperature curve."""
        min_temp = 20
        max_temp = 30

        # Test at 3 hours from noon (where wave spread has noticeable effect)
        hours_from_noon = 3

        # Standard wave spread (1.0)
        temp_standard = calculate_sine_wave_temp(
            min_temp, max_temp, hours_from_noon, 1.0
        )

        # Steeper wave spread (1.5) - should be closer to midpoint
        temp_steep = calculate_sine_wave_temp(min_temp, max_temp, hours_from_noon, 1.5)

        # Gentler wave spread (0.7) - should be closer to max temp
        temp_gentle = calculate_sine_wave_temp(min_temp, max_temp, hours_from_noon, 0.7)

        # With steeper spread, temperature should be closer to midpoint
        # With gentler spread, temperature should be closer to max temp
        assert abs(temp_steep - 25) < abs(temp_standard - 25)
        assert temp_gentle > temp_standard
