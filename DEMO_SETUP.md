# Daily Temperature Wave - Demo Setup Guide

This guide helps you set up a basic Home Assistant environment to test the Daily Temperature Wave component.

## Option 1: Quick Docker Setup (Recommended)

### Prerequisites
- Docker installed on your system
- Basic command line knowledge

### Setup Steps

1. **Create a docker-compose.yml file**:

```bash
mkdir ha-demo
cd ha-demo
```

```yaml
# docker-compose.yml
version: '3'
services:
  homeassistant:
    image: "ghcr.io/home-assistant/home-assistant:stable"
    container_name: homeassistant
    network_mode: host
    environment:
      - TZ=America/New_York
    volumes:
      - ./config:/config
      - ../custom_components:/config/custom_components
    restart: unless-stopped
    privileged: true
```

2. **Start Home Assistant**:

```bash
docker-compose up -d
```

3. **Access Home Assistant**:
   - Open your browser to `http://localhost:8123`
   - Complete the initial setup

4. **Install the component**:
   - The component should be automatically available since we mounted the custom_components directory
   - Go to Settings → Devices & Services → Add Integration
   - Search for "Daily Temperature Wave" and complete the setup

## Option 2: Manual Python Setup

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)

### Setup Steps

1. **Create a virtual environment**:

```bash
python -m venv venv
ha-demo\venv\Scripts\activate
```

2. **Install Home Assistant**:

```bash
pip install homeassistant
```

3. **Create configuration directory**:

```bash
mkdir config
```

4. **Create configuration.yaml**:

```yaml
# config/configuration.yaml
default_config:

# Add the custom component
logger:
  default: info
  logs:
    custom_components.daily_temperature_wave: debug
```

5. **Copy the custom component**:

```bash
# Copy from our project to the config directory
copy-item "custom_components" "config\custom_components" -Recurse
```

6. **Start Home Assistant**:

```bash
hass -c config
```

7. **Access Home Assistant**:
   - Open your browser to `http://localhost:8123`
   - Complete the initial setup

## Option 3: Home Assistant Core (Minimal)

For a lightweight test without the full UI:

```bash
# Install Home Assistant Core
pip install homeassistant

# Create a test script
python test_component.py
```

Here's a simple test script:

```python
# test_component.py
import asyncio
from datetime import datetime
from homeassistant.core import HomeAssistant
from custom_components.daily_temperature_wave.sensor import DailyTemperatureWaveSensor
from custom_components.daily_temperature_wave.const import SENSOR_CURRENT

async def test_component():
    # Create a mock config entry
    class MockConfigEntry:
        def __init__(self):
            self.entry_id = "test"
            self.data = {
                "min_temp": "20C",
                "max_temp": "30C",
                "wave_spread": 1.0,
                "step_resolution": "1F",
                "step_interval": 30,
                "unit_system": "metric",
            }
            self.options = {}
    
    # Create sensor
    config_entry = MockConfigEntry()
    sensor_desc = next(desc for desc in DailyTemperatureWaveSensor.SENSOR_DESCRIPTIONS if desc.key == SENSOR_CURRENT)
    sensor = DailyTemperatureWaveSensor(config_entry, sensor_desc)
    
    # Mock Home Assistant
    sensor.hass = type('MockHA', (), {
        'config': type('MockConfig', (), {'time_zone': None})()
    })()
    
    # Test temperature calculation
    from custom_components.daily_temperature_wave.utils.solar import get_solar_noon
    from datetime import time
    
    solar_noon = get_solar_noon(sensor.hass, None)
    temp = sensor._calculate_current_temperature(sensor.hass, solar_noon)
    
    print(f"Current temperature: {temp}°C")
    print(f"Solar noon: {solar_noon}")
    print("✅ Component test successful!")

if __name__ == "__main__":
    asyncio.run(test_component())
```

## Configuration Examples

### Basic Configuration

```yaml
# configuration.yaml
daily_temperature_wave:
  min_temp: 20C
  max_temp: 30C
  wave_spread: 1.0
  unit_system: metric
```

### Advanced Configuration

```yaml
# configuration.yaml
daily_temperature_wave:
  min_temp: 15C
  max_temp: 35C
  wave_spread: 1.2
  step_resolution: 0.5C
  step_interval: 30
  unit_system: metric
  solar_noon_override: "12:30"
```

## Expected Sensors

After setup, you should see these sensors in Home Assistant:

- `sensor.daily_temperature_wave_current` - Current temperature
- `sensor.daily_temperature_wave_current_step` - Stepwise temperature
- `sensor.daily_temperature_wave_forecast_24h` - 24-hour forecast
- `sensor.daily_temperature_wave_forecast_7d` - 7-day forecast
- `sensor.daily_temperature_wave_visual` - Visualization data
- `binary_sensor.daily_temperature_wave_rising` - Temperature trend

## Troubleshooting

### Component not showing up?
- Check that the `custom_components` directory is correctly mounted/copied
- Verify the directory structure: `config/custom_components/daily_temperature_wave/`
- Check Home Assistant logs for errors
- Restart Home Assistant after installation

### Configuration issues?
- Ensure `min_temp` < `max_temp`
- Use valid temperature formats (e.g., "20C", "68F")
- Check that `wave_spread` is between 0.1 and 5.0

## Demo Video

For a visual demonstration, you can:
1. Set up the component as described above
2. Add the sensors to a Lovelace dashboard
3. Create a simple card to display the current temperature and visualization

Example Lovelace card:

```yaml
# In your Lovelace UI
cards:
  - type: entities
    title: Daily Temperature Wave
    entities:
      - sensor.daily_temperature_wave_current
      - sensor.daily_temperature_wave_current_step
      - binary_sensor.daily_temperature_wave_rising
      - sensor.daily_temperature_wave_visual
```

## Support

If you encounter issues during setup:
- Check the Home Assistant logs
- Verify file permissions
- Ensure Docker/venv is properly configured
- Consult the main README for troubleshooting tips

**Enjoy your Daily Temperature Wave demo!** 🌡️🌞