# Daily Temperature Wave - Home Assistant Custom Component

![GitHub release (latest by date)](https://img.shields.io/github/v/release/yourusername/ha-daily-temperature-wave)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/ha-daily-temperature-wave)
![License](https://img.shields.io/github/license/yourusername/ha-daily-temperature-wave)

A custom Home Assistant component that generates a daily temperature wave using sine wave calculations. Perfect for simulating outdoor temperatures, testing HVAC systems, or creating dynamic temperature patterns.

## Features

- **Sine Wave Temperature**: Smooth temperature curve peaking at solar noon
- **Configurable Range**: Set minimum and maximum temperatures
- **Wave Spread Control**: Adjust the slope of the temperature curve
- **Mixed Unit Support**: Use Celsius and Fahrenheit in the same configuration
- **Stepwise Mode**: Optional stepped temperature changes
- **Comprehensive Forecasts**: 24-hour and 7-day forecasts
- **Visual Curve Display**: SVG visualization of the temperature wave
- **Rising/Falling Sensor**: Binary sensor indicating temperature trend
- **Solar Noon Detection**: Automatic with fallback to wall clock noon
- **WebUI Configuration**: Easy setup through Home Assistant UI

## Installation

### HACS (Recommended)

1. **Add this repository** to HACS:
   - Go to HACS → Integrations
   - Click the three-dot menu → Custom repositories
   - Add `https://github.com/yourusername/ha-daily-temperature-wave` as a custom repository
   - Select category "Integration"

2. **Install the integration**:
   - Search for "Daily Temperature Wave" in HACS
   - Click "Download"
   - Restart Home Assistant

3. **Add the integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration" → Search for "Daily Temperature Wave"
   - Follow the configuration steps

### Manual Installation

1. **Download the component**:
   ```bash
   git clone https://github.com/yourusername/ha-daily-temperature-wave.git
   ```

2. **Copy the files**:
   ```bash
   cp -r ha-daily-temperature-wave/custom_components/daily_temperature_wave <your_config_dir>/custom_components/
   ```

3. **Restart Home Assistant**

4. **Add the integration** through the UI as described above

## Configuration

### WebUI Configuration (Recommended)

The component provides a full WebUI configuration flow:

1. Go to Settings → Devices & Services
2. Click "Add Integration" → Search for "Daily Temperature Wave"
3. Fill in the configuration parameters:

### YAML Configuration (Optional)

You can also configure the component via `configuration.yaml`:

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

## Development

### Running Tests

```bash
# Run unit tests
python -m unittest tests.test_utils tests.test_sensor

# Run core functionality tests
python -m unittest tests.test_core
```

### Code Formatting

This project uses **Black** and **isort** for code formatting:

```bash
# Format code with Black
python -m black .

# Sort imports with isort
python -m isort .

# Run both formatting tools
python -m black . && python -m isort .
```

### Pre-commit Hooks

The project includes pre-commit hooks for automated code quality checks:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run all hooks
pre-commit run --all-files
```

### Configuration Files

- `pyproject.toml`: Black, isort, and other tool configurations
- `.pre-commit-config.yaml`: Pre-commit hook configurations
- `.gitignore`: Git ignore patterns

### Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** following the existing code style
4. **Run formatting**: `python -m black . && python -m isort .`
5. **Write tests** for new functionality
6. **Run tests**: Ensure all tests pass
7. **Submit a pull request** with a clear description

### Code Quality Standards

- **Black** code formatting
- **isort** import sorting
- **Type hints** for better code clarity
- **Comprehensive tests** for all functionality
- **Documentation** for public APIs
- **MIT License** compliance

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for the full license text.

### Key Terms
- **Free to use**: For personal and commercial projects
- **Open source**: Source code is available and modifiable
- **No warranty**: Software provided "as is" without guarantees
- **Attribution**: Copyright notice must be preserved

## Support

For issues, questions, or feature requests:

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Community Forum**: Home Assistant community forums

## Changelog

### 1.0.0 (Initial Release)
- Basic sine wave temperature generation
- Configurable temperature range
- WebUI configuration support
- Multiple sensor types
- Unit conversion support

### Future Plans
- Enhanced visualization options
- Historical data tracking
- Integration with weather providers
- Custom wave shape profiles

## Acknowledgements

- Home Assistant community for inspiration and support
- Open source contributors who make this possible

---

**Enjoy your Daily Temperature Wave!** 🌡️🌞