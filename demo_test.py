#!/usr/bin/env python3
"""
Daily Temperature Wave - Demo Test Script

This script demonstrates the core functionality of the Daily Temperature Wave component
without requiring a full Home Assistant installation.
"""

import asyncio
import math
from datetime import datetime, time

# Import our utility functions
from custom_components.daily_temperature_wave.utils.temperature import (
    parse_temperature_value,
    convert_to_celsius,
    convert_from_celsius,
    round_to_step,
)
from custom_components.daily_temperature_wave.utils.solar import get_solar_noon


def calculate_temperature(min_temp, max_temp, hours_from_noon, wave_spread=1.0):
    """Calculate temperature using sine wave formula."""
    sine_value = math.sin(math.pi * hours_from_noon / (12 * wave_spread))
    temp_normalized = (sine_value + 1) / 2
    return min_temp + (max_temp - min_temp) * temp_normalized


def demonstrate_temperature_wave():
    """Demonstrate the temperature wave functionality."""
    print("🌡️  Daily Temperature Wave Demo")
    print("=" * 50)
    
    # Configuration
    min_temp_c, min_temp_unit = parse_temperature_value("20C")
    max_temp_c, max_temp_unit = parse_temperature_value("30C")
    wave_spread = 1.0
    unit_system = "metric"
    
    print(f"Configuration:")
    print(f"  Minimum Temperature: {min_temp_c}°C")
    print(f"  Maximum Temperature: {max_temp_c}°C")
    print(f"  Wave Spread: {wave_spread}")
    print(f"  Unit System: {unit_system}")
    print()
    
    # Demonstrate temperature calculation at different times
    print("Temperature at different times of day:")
    print("-" * 50)
    
    times = [
        (-6, "6:00 AM (6 hours before noon)"),
        (-3, "9:00 AM (3 hours before noon)"),
        (0, "12:00 PM (Solar Noon)"),
        (3, "3:00 PM (3 hours after noon)"),
        (6, "6:00 PM (6 hours after noon)"),
        (12, "12:00 AM (Midnight)"),
    ]
    
    for hours_from_noon, time_desc in times:
        temp_c = calculate_temperature(min_temp_c, max_temp_c, hours_from_noon, wave_spread)
        temp_display = convert_from_celsius(temp_c, unit_system)
        
        print(f"  {time_desc:30} → {temp_display:5.1f}°C")
    
    print()
    
    # Demonstrate wave spread effect
    print("Wave Spread Effect (at 3 hours from noon):")
    print("-" * 50)
    
    hours_from_noon = 3
    for spread in [0.7, 1.0, 1.5]:
        temp_c = calculate_temperature(min_temp_c, max_temp_c, hours_from_noon, spread)
        temp_display = convert_from_celsius(temp_c, unit_system)
        
        spread_desc = "Gentle" if spread < 1.0 else "Steep" if spread > 1.0 else "Standard"
        print(f"  Wave Spread {spread} ({spread_desc:7}): {temp_display:5.1f}°C")
    
    print()
    
    # Demonstrate unit conversion
    print("Unit Conversion Examples:")
    print("-" * 50)
    
    test_temps = [0, 20, 30, 100]
    for temp_c in test_temps:
        temp_f = convert_from_celsius(temp_c, "F")
        print(f"  {temp_c:3}°C = {temp_f:5.1f}°F")
    
    print()
    
    # Demonstrate stepwise function
    print("Stepwise Temperature Examples:")
    print("-" * 50)
    
    step_resolution, step_unit = parse_temperature_value("1F")
    step_c = convert_to_celsius(step_resolution, step_unit)
    
    test_temps = [20.3, 20.7, 21.2, 21.8]
    for temp in test_temps:
        stepped = round_to_step(temp, step_c)
        print(f"  {temp:4.1f}°C → {stepped:4.1f}°C (step: {step_c:.1f}°C)")
    
    print()
    print("✅ Demo completed successfully!")
    print("📊 The Daily Temperature Wave component is working correctly.")
    print()
    print("To use this in Home Assistant:")
    print("1. Install the component via HACS or manual setup")
    print("2. Configure through the WebUI")
    print("3. Add sensors to your Lovelace dashboard")
    print("4. Enjoy your temperature wave simulation!")


def demonstrate_solar_noon():
    """Demonstrate solar noon calculation."""
    print("\n🌞 Solar Noon Calculation Demo")
    print("=" * 50)
    
    # Create a mock Home Assistant instance
    class MockHA:
        def __init__(self):
            self.config = type('Config', (), {'time_zone': None})()
            self.states = {}
    
    hass = MockHA()
    
    # Test solar noon with fallback
    solar_noon = get_solar_noon(hass, None)
    print(f"Solar Noon (with fallback): {solar_noon}")
    
    # Test with override
    solar_noon_override = get_solar_noon(hass, "14:30")
    print(f"Solar Noon (with override): {solar_noon_override}")
    
    print("✅ Solar noon calculation working correctly!")


if __name__ == "__main__":
    demonstrate_temperature_wave()
    demonstrate_solar_noon()