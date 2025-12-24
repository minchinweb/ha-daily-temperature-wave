# Daily Temperature Wave - Home Assistant Custom Component

![GitHub release (latest by date)](https://img.shields.io/github/v/release/minchinweb/ha-daily-temperature-wave)
![GitHub last commit](https://img.shields.io/github/last-commit/minchinweb/ha-daily-temperature-wave)
![License](https://img.shields.io/github/license/minchinweb/ha-daily-temperature-wave)
![GitHub Actions](https://github.com/minchinweb/ha-daily-temperature-wave/actions/workflows/python-package.yml/badge.svg)

Provides a Daily Temperature (sine) Wave as a custom Home Assistant component.
Can be used as a heating/cooling target.

By default, the temperature will peak at solar noon (which can be 1 1/2 or more
from "wall clock" noon). Also provides a "step wise" version that can be used
in lower resolution settings (e.g. setting up an Ecobee schedule, which only
lets you set temperatures for each 1/2 hour, and only in 1&deg;F resolution).

Sensors include:

- current temperature
- rising/failing "switch"
- 24-hour and 7-day "forecasts"

## Installation

Semi-automatically:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=minchinweb&repository=ha-daily-temperature-wave&category=integration)

[![add integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=daily_temperature_ave)

or manually:

Add as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/) in HACS:

```test
https://github.com/minchinweb/ha-daily-temperature-wave
```

Then search for "Daily Temperature Wave" in HACS and install through HACS.

Finally, add the integration, via Settings --> Devices & Services --> "Add
Integration" --> Search for "Daily Temperature Wave"


## Configuration

It is likely easiest to configure through the Web UI, but a full YAML
configuration would look like this:

```yaml
daily_temperature_wave:
  min_temp: 20C      # Minimum temperature (default: 20°C)
  max_temp: 30C      # Maximum temperature (default: 30°C)
  wave_spread: 1.2   # Wave spread factor (default: 1.0)
  step_resolution: 1F  # Step resolution for stepwise mode (default: 1°F)
  step_interval: 30   # Step interval in minutes (default: 30)
  unit_system: metric # Unit system (metric/imperial, default: metric)
  solar_noon_override: "12:30"  # Optional: Manual solar noon override
```

<!-- rewritten up to here.. -->

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_temp` | string | "20C" | Minimum temperature (supports "20C" or "68F" format) |
| `max_temp` | string | "30C" | Maximum temperature (supports "30C" or "86F" format) |
| `wave_spread` | float | 1.0 | Controls the slope of the sine wave (1.0 = standard, >1.0 = steeper) |
| `step_resolution` | string | "1F" | Temperature step size for stepwise mode (supports "1F" or "0.5C") |
| `step_interval` | int | 30 | Time between step changes in minutes |
| `unit_system` | string | "metric" | Display unit system ("metric" or "imperial") |
| `solar_noon_override` | string | None | Manual override for solar noon time (format: "HH:MM") |

## Sensors

The component creates the following sensors:

### Temperature Sensors

| Sensor | Description | Unit |
|--------|-------------|------|
| `sensor.daily_temperature_wave_current` | Current temperature from sine wave | °C or °F |
| `sensor.daily_temperature_wave_current_step` | Current temperature with stepwise changes | °C or °F |

### Forecast Sensors

| Sensor | Description | Format |
|--------|-------------|--------|
| `sensor.daily_temperature_wave_forecast_24h` | 24-hour hourly forecast | JSON array |
| `sensor.daily_temperature_wave_forecast_24h_step` | 24-hour stepwise forecast | JSON array |
| `sensor.daily_temperature_wave_forecast_7d` | 7-day daily forecast | JSON array |
| `sensor.daily_temperature_wave_forecast_7d_step` | 7-day stepwise forecast | JSON array |

### Visualization Sensor

| Sensor | Description | Format |
|--------|-------------|--------|
| `sensor.daily_temperature_wave_visual` | Temperature curve visualization data | JSON |

### Binary Sensor

| Sensor | Description | State |
|--------|-------------|-------|
| `binary_sensor.daily_temperature_wave_rising` | Indicates if temperature is rising | on/off |

## Usage Examples

### Basic Temperature Display

```yaml
# In your Lovelace UI
cards:
  - type: entities
    entities:
      - sensor.daily_temperature_wave_current
      - sensor.daily_temperature_wave_current_step
      - binary_sensor.daily_temperature_wave_rising
```

### Temperature Curve Visualization

```yaml
# Custom card using the visualization data
cards:
  - type: custom:your-custom-card
    data: >-
      {{ state_attr('sensor.daily_temperature_wave_visual', 'svg') }}
```

### Forecast Display

```yaml
# Display 24-hour forecast
cards:
  - type: entities
    entities:
      - type: section
        label: 24-Hour Forecast
      - type: custom:auto-entities
        card:
          type: entities
        filter:
          include:
            - entity_id: sensor.daily_temperature_wave_forecast_24h
              options:
                secondary_info: last-changed
```

## Advanced Configuration

### Wave Spread Examples

- **Standard Wave** (`wave_spread: 1.0`): Normal sine wave with 12-hour period
- **Steep Wave** (`wave_spread: 1.5`): Steeper slope, narrower peak around solar noon
- **Gentle Wave** (`wave_spread: 0.7`): Gentler slope, wider temperature range

### Mixed Unit Configuration

```yaml
daily_temperature_wave:
  min_temp: 20C      # Celsius for main temperatures
  max_temp: 30C      # Celsius for main temperatures
  step_resolution: 1F  # But use Fahrenheit for step resolution
  unit_system: metric # Display in metric
```

## Troubleshooting

### Solar Noon Detection Issues

If the sun integration is not available, the component automatically falls back to wall clock noon (12:00). You can also manually override:

```yaml
daily_temperature_wave:
  solar_noon_override: "12:30"  # Use 12:30 PM as solar noon
```

### Temperature Not Updating

- Check that the component is properly installed and configured
- Verify that Home Assistant has restarted after installation
- Check the logs for any errors: `Settings → System → Logs`

### Invalid Configuration

If you see configuration errors:
- Ensure `min_temp` < `max_temp`
- Use valid temperature formats (e.g., "20C", "68F", or plain numbers)
- Check that `wave_spread` is between 0.1 and 5.0

## Contribution Hints

### Running Tests Locally

```bash
# Run unit tests
python -m unittest tests.test_utils tests.test_sensor

# Run core functionality tests
python -m unittest tests.test_core
```

### Code Formatting

This project uses **Black** and **isort** for code formatting:


### Pre-commit Hooks

The project includes pre-commit hooks for automated code quality checks:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run all hooks
pre-commit run --all-files
```

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for the full license text.

## Support

For issues, questions, or feature requests:

- **GitHub Issues**: [Report bugs](https://github.com/minchinweb/ha-daily-temperature-wave/issues)
- **Discussions**: [Ask questions](https://github.com/minchinweb/ha-daily-temperature-wave/discussions)
- **Community Forum**: Home Assistant community forums

## Changelog

### v1.0.0 -- 2025-12-24 (Initial Release)

- Basic sine wave temperature generation
- Configurable temperature range
- WebUI configuration support
- Multiple sensor types
- Unit conversion support

---

**Enjoy your Daily Temperature Wave!** 🌡️🌞
