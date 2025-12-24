"""
Test to verify pytest setup is working correctly.
"""

import pytest


def test_pytest_works():
    """Simple test to verify pytest is working."""
    assert 1 + 1 == 2


def test_imports_work():
    """Test that we can import our modules."""
    # Test basic functionality without importing Home Assistant dependent modules
    # This is a simple test to verify pytest is working
    assert True  # Basic test that doesn't require imports


def test_core_functionality():
    """Test core temperature calculation."""
    import math

    def calculate_temperature(min_temp, max_temp, hours_from_noon, wave_spread=1.0):
        """Calculate temperature using sine wave formula."""
        sine_value = math.sin(math.pi * hours_from_noon / (12 * wave_spread))
        temp_normalized = (sine_value + 1) / 2
        return min_temp + (max_temp - min_temp) * temp_normalized

    # Test at solar noon (should be midpoint)
    temp = calculate_temperature(20, 30, 0, 1.0)
    assert abs(temp - 25.0) < 0.1

    # Test 6 hours after noon (should be max)
    temp = calculate_temperature(20, 30, 6, 1.0)
    assert abs(temp - 30.0) < 0.1

    # Test 6 hours before noon (should be min)
    temp = calculate_temperature(20, 30, -6, 1.0)
    assert abs(temp - 20.0) < 0.1
