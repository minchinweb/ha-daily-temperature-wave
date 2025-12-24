#!/usr/bin/env python3
"""
Daily Temperature Wave - Simple Demo

This script demonstrates the core sine wave temperature calculation
without requiring Home Assistant or external dependencies.
"""

import math
from datetime import time


def parse_temperature_value(value):
    """Parse temperature values with optional unit suffixes."""
    if isinstance(value, (int, float)):
        return float(value), "C"
    
    value_str = str(value).strip().upper()
    if value_str.endswith("F"):
        return float(value_str[:-1]), "F"
    elif value_str.endswith("C"):
        return float(value_str[:-1]), "C"
    else:
        return float(value_str), "C"


def convert_to_celsius(value, unit):
    """Convert temperature to Celsius."""
    if unit.upper() == "F":
        return (value - 32) * 5/9
    return value


def convert_from_celsius(value, target_unit):
    """Convert temperature from Celsius to target unit."""
    if target_unit.upper() == "F":
        return value * 9/5 + 32
    return value


def round_to_step(value, step):
    """Round temperature value to nearest step."""
    if step <= 0:
        return value
    return round(value / step) * step


def calculate_temperature(min_temp, max_temp, hours_from_noon, wave_spread=1.0):
    """Calculate temperature using sine wave formula."""
    sine_value = math.sin(math.pi * hours_from_noon / (12 * wave_spread))
    temp_normalized = (sine_value + 1) / 2
    return min_temp + (max_temp - min_temp) * temp_normalized


def get_solar_noon_fallback(solar_noon_override=None):
    """Get solar noon with fallback to wall clock noon."""
    if solar_noon_override:
        try:
            hour, minute = map(int, solar_noon_override.split(":"))
            return time(hour, minute)
        except:
            pass
    return time(12, 0)


def main():
    """Main demo function."""
    print("Daily Temperature Wave - Simple Demo")
    print("=" * 60)
    print()
    
    # Configuration
    min_temp_str = "20C"
    max_temp_str = "30C"
    wave_spread = 1.0
    unit_system = "metric"
    
    min_temp_c, _ = parse_temperature_value(min_temp_str)
    max_temp_c, _ = parse_temperature_value(max_temp_str)
    
    print("Configuration:")
    print(f"   Minimum Temperature: {min_temp_c}C ({min_temp_str})")
    print(f"   Maximum Temperature: {max_temp_c}C ({max_temp_str})")
    print(f"   Wave Spread: {wave_spread}")
    print(f"   Unit System: {unit_system}")
    print()
    
    # Solar noon
    solar_noon = get_solar_noon_fallback()
    print(f"Solar Noon: {solar_noon.hour:02d}:{solar_noon.minute:02d}")
    print()
    
    # Temperature wave demonstration
    print("Temperature Wave (24-hour cycle):")
    print("-" * 60)
    
    times = [
        (-12, "12:00 AM"),
        (-9, "3:00 AM"),
        (-6, "6:00 AM"),
        (-3, "9:00 AM"),
        (0, "12:00 PM"),
        (3, "3:00 PM"),
        (6, "6:00 PM"),
        (9, "9:00 PM"),
        (12, "12:00 AM"),
    ]
    
    for hours_from_noon, time_str in times:
        temp_c = calculate_temperature(min_temp_c, max_temp_c, hours_from_noon, wave_spread)
        temp_display = convert_from_celsius(temp_c, unit_system)
        
        # Calculate position in wave (0-100%)
        wave_position = (math.sin(math.pi * hours_from_noon / (12 * wave_spread)) + 1) / 2 * 100
        
        bar_length = int(wave_position / 2)
        bar = "#" * bar_length + "-" * (50 - bar_length)
        
        print(f"   {time_str:8} | {bar} | {temp_display:5.1f}C")
    
    print()
    
    # Wave spread comparison
    print("Wave Spread Comparison (at 3:00 PM):")
    print("-" * 60)
    
    hours_from_noon = 3
    spreads = [0.5, 0.7, 1.0, 1.5, 2.0]
    
    for spread in spreads:
        temp_c = calculate_temperature(min_temp_c, max_temp_c, hours_from_noon, spread)
        temp_display = convert_from_celsius(temp_c, unit_system)
        
        desc = "Very Gentle" if spread <= 0.5 else "Gentle" if spread < 1.0 else "Standard" if spread == 1.0 else "Steep" if spread < 2.0 else "Very Steep"
        print(f"   Spread {spread:4.1f} ({desc:12}): {temp_display:5.1f}C")
    
    print()
    
    # Unit conversion demo
    print("Unit Conversion Examples:")
    print("-" * 60)
    
    test_temps = [0, 10, 20, 30, 100]
    for temp_c in test_temps:
        temp_f = convert_from_celsius(temp_c, "F")
        print(f"   {temp_c:3}C = {temp_f:5.1f}F")
    
    print()
    
    # Stepwise demo
    print("Stepwise Temperature (1°F steps):")
    print("-" * 60)
    
    step_resolution, step_unit = parse_temperature_value("1F")
    step_c = convert_to_celsius(step_resolution, step_unit)
    
    test_temps = [20.1, 20.6, 21.3, 21.8, 22.4]
    for temp in test_temps:
        stepped = round_to_step(temp, step_c)
        print(f"   {temp:4.1f}C -> {stepped:4.1f}C")
    
    print()
    
    # Summary
    print("SUCCESS: Demo completed successfully!")
    print()
    print("Key Features Demonstrated:")
    print("   * Sine wave temperature generation")
    print("   * Configurable temperature range")
    print("   * Wave spread parameter")
    print("   * Unit conversion (Celsius <-> Fahrenheit)")
    print("   * Stepwise temperature changes")
    print("   * Solar noon handling")
    print()
    print("To use this in Home Assistant:")
    print("   1. Install the component via HACS")
    print("   2. Configure through the WebUI")
    print("   3. Add sensors to your dashboard")
    print("   4. Enjoy your temperature wave simulation!")
    print()
    print("Daily Temperature Wave - Ready for Home Assistant!")


if __name__ == "__main__":
    main()