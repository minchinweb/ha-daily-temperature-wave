"""
Constants for the Daily Temperature Wave component.
"""

# Domain
DOMAIN = "daily_temperature_wave"

# Platforms
PLATFORMS = ["sensor", "binary_sensor"]

# Default configuration values
DEFAULT_MIN_TEMP = "20C"  # 20°C
DEFAULT_MAX_TEMP = "30C"  # 30°C
DEFAULT_WAVE_SPREAD = 1.0
DEFAULT_STEP_RESOLUTION = "1F"  # 1°F steps
DEFAULT_STEP_INTERVAL = 30  # minutes
DEFAULT_UNIT_SYSTEM = "metric"
DEFAULT_SOLAR_NOON_OVERRIDE = None

# Configuration keys
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_WAVE_SPREAD = "wave_spread"
CONF_STEP_RESOLUTION = "step_resolution"
CONF_STEP_INTERVAL = "step_interval"
CONF_UNIT_SYSTEM = "unit_system"
CONF_SOLAR_NOON_OVERRIDE = "solar_noon_override"

# Sensor names
SENSOR_CURRENT = "current"
SENSOR_CURRENT_STEP = "current_step"
SENSOR_FORECAST_24H = "forecast_24h"
SENSOR_FORECAST_24H_STEP = "forecast_24h_step"
SENSOR_FORECAST_7D = "forecast_7d"
SENSOR_FORECAST_7D_STEP = "forecast_7d_step"
SENSOR_VISUAL = "visual"

BINARY_SENSOR_RISING = "rising"

# Icons
ICON_CURRENT = "mdi:thermometer"
ICON_FORECAST = "mdi:weather-partly-cloudy"
ICON_VISUAL = "mdi:chart-line"
ICON_RISING = "mdi:arrow-up"
ICON_FALLING = "mdi:arrow-down"

# Update intervals
SCAN_INTERVAL = timedelta(minutes=1)

# Temperature unit constants
TEMP_CELSIUS = "°C"
TEMP_FAHRENHEIT = "°F"

# Visualization constants
VISUAL_WIDTH = 300
VISUAL_HEIGHT = 150
VISUAL_PADDING = 10
VISUAL_COLOR = "#3498db"
VISUAL_CURRENT_COLOR = "#e74c3c"
VISUAL_BACKGROUND = "#f5f5f5"
