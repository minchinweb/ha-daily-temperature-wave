"""
Solar utility functions for the Daily Temperature Wave component.
"""

import logging
from datetime import datetime, time
from typing import Optional

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


def get_solar_noon(
    hass: HomeAssistant, solar_noon_override: Optional[str] = None
) -> time:
    """
    Get solar noon time with fallback to wall clock noon.

    Args:
        hass: Home Assistant instance
        solar_noon_override: Optional manual override for solar noon

    Returns:
        Solar noon time (or wall clock noon if sun integration unavailable)
    """
    # Check for manual override first
    if solar_noon_override:
        try:
            # Parse override time (format: "HH:MM")
            hour, minute = map(int, solar_noon_override.split(":"))
            return time(hour, minute)
        except (ValueError, AttributeError) as e:
            _LOGGER.warning(
                "Invalid solar noon override format: %s. Using fallback.",
                solar_noon_override,
            )

    # Try to get solar noon from sun integration
    try:
        sun_entity = hass.states.get("sun.sun")
        if sun_entity and sun_entity.state == "above_horizon":
            # Calculate solar noon from sun attributes
            next_setting = sun_entity.attributes.get("next_setting")
            next_rising = sun_entity.attributes.get("next_rising")

            if next_setting and next_rising:
                setting_time = datetime.fromisoformat(next_setting)
                rising_time = datetime.fromisoformat(next_rising)

                # Solar noon is halfway between sunrise and sunset
                solar_noon_time = rising_time + (setting_time - rising_time) / 2
                return solar_noon_time.time()
    except Exception as e:
        _LOGGER.debug("Could not calculate solar noon from sun integration: %s", e)

    # Fallback to wall clock noon
    _LOGGER.info("Using wall clock noon (12:00) as solar noon")
    return time(12, 0)


def get_current_solar_position(hass: HomeAssistant, solar_noon: time) -> float:
    """
    Get current position in the solar day (0.0 = solar noon, -6.0 = 6 hours before, +6.0 = 6 hours after).

    Args:
        hass: Home Assistant instance
        solar_noon: Solar noon time

    Returns:
        Hours from solar noon (-12.0 to +12.0)
    """
    now = datetime.now(hass.config.time_zone)
    current_time = now.time()

    # Calculate hours from solar noon
    current_hours = current_time.hour + current_time.minute / 60
    solar_noon_hours = solar_noon.hour + solar_noon.minute / 60

    # Handle midnight crossing
    hours_from_noon = current_hours - solar_noon_hours

    # Normalize to -12 to +12 range
    if hours_from_noon > 12:
        hours_from_noon -= 24
    elif hours_from_noon < -12:
        hours_from_noon += 24

    return hours_from_noon


def is_temperature_rising(
    hass: HomeAssistant, solar_noon: time, wave_spread: float = 1.0
) -> bool:
    """
    Determine if temperature is currently rising or falling.

    Args:
        hass: Home Assistant instance
        solar_noon: Solar noon time
        wave_spread: Wave spread factor

    Returns:
        True if temperature is rising, False if falling
    """
    hours_from_noon = get_current_solar_position(hass, solar_noon)

    # Calculate the effective period based on wave spread
    effective_period = 12 * wave_spread

    # Temperature is rising when we're in the first half of the wave period
    # (from min to max, which is from -effective_period/2 to +effective_period/2 relative to solar noon)
    return -effective_period / 2 <= hours_from_noon <= effective_period / 2
