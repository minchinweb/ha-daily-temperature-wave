# Copyright (c) 2025 William Minchin
"""Constants for the Daily Temperature Wave integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "daily_temperature_wave"

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]

# Configuration keys
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_WAVE_SPREAD = "wave_spread"
CONF_STEP_RESOLUTION = "step_resolution"
CONF_STEP_INTERVAL = "step_interval"
CONF_SOLAR_NOON_OVERRIDE = "solar_noon_override"

# Defaults
DEFAULT_NAME = "Daily Temperature Wave"
DEFAULT_MIN_TEMP = "20C"
DEFAULT_MAX_TEMP = "30C"
DEFAULT_WAVE_SPREAD = 1.0
DEFAULT_STEP_RESOLUTION = "1F"
DEFAULT_STEP_INTERVAL = 30  # minutes

# Entity keys (also the translation keys, and the suffix of the unique ID)
SENSOR_CURRENT = "current"
SENSOR_CURRENT_STEP = "current_step"
SENSOR_FORECAST_24H = "forecast_24h"
SENSOR_FORECAST_24H_STEP = "forecast_24h_step"
SENSOR_FORECAST_7D = "forecast_7d"
SENSOR_FORECAST_7D_STEP = "forecast_7d_step"
SENSOR_VISUAL = "visual"
BINARY_SENSOR_RISING = "rising"

FORECAST_DAYS = 7
