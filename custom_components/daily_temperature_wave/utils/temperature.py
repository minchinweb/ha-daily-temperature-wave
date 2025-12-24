"""
Temperature utility functions for the Daily Temperature Wave component.
"""

import re
from typing import Tuple, Union

from ..const import TEMP_CELSIUS, TEMP_FAHRENHEIT


def parse_temperature_value(value: Union[str, int, float]) -> Tuple[float, str]:
    """
    Parse temperature values with optional unit suffixes.

    Args:
        value: Temperature value as string (e.g., "20C", "68F") or number

    Returns:
        Tuple of (numeric_value, unit) where unit is 'C' or 'F'
    """
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


def convert_to_celsius(value: float, unit: str) -> float:
    """
    Convert temperature to Celsius.

    Args:
        value: Temperature value
        unit: Unit ('C' or 'F')

    Returns:
        Temperature in Celsius
    """
    if unit.upper() == "F":
        return (value - 32) * 5 / 9
    return value


def convert_from_celsius(value: float, target_unit: str) -> float:
    """
    Convert temperature from Celsius to target unit.

    Args:
        value: Temperature value in Celsius
        target_unit: Target unit ('C' or 'F')

    Returns:
        Temperature in target unit
    """
    if target_unit.upper() == "F":
        return value * 9 / 5 + 32
    return value


def round_to_step(value: float, step: float) -> float:
    """
    Round temperature value to nearest step.

    Args:
        value: Temperature value
        step: Step size

    Returns:
        Rounded temperature value
    """
    if step <= 0:
        return value
    return round(value / step) * step


def get_unit_symbol(unit: str) -> str:
    """
    Get the unit symbol for display.

    Args:
        unit: Unit ('C' or 'F')

    Returns:
        Unit symbol
    """
    if unit.upper() == "F":
        return TEMP_FAHRENHEIT
    return TEMP_CELSIUS


def parse_step_resolution(step_resolution: str) -> Tuple[float, str]:
    """
    Parse step resolution with optional unit suffix.

    Args:
        step_resolution: Step resolution as string (e.g., "1F", "0.5C")

    Returns:
        Tuple of (step_value, unit)
    """
    return parse_temperature_value(step_resolution)
