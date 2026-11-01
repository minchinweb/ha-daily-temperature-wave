# Development

## Tooling

The project uses [uv](https://docs.astral.sh/uv/) for its environment and
[invoke](https://www.pyinvoke.org/) for tasks:

```bash
uv sync                  # install everything in uv.lock into .venv
uv run invoke --list     # list tasks
uv run invoke format     # apply lint fixes and formatting (ruff, taplo)
uv run invoke check      # lint + tests, the same as CI
```

The tests use
[`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component),
which installs Home Assistant itself. Home Assistant does not support Windows,
so on Windows run the test suite under WSL (`uv run pytest` from the repo
inside WSL). The pure wave-math tests (`tests/test_wave.py`) run anywhere.

## Trying it in a real Home Assistant

### Docker

From a folder next to this repo:

```yaml
# docker-compose.yml
services:
  homeassistant:
    image: "ghcr.io/home-assistant/home-assistant:stable"
    container_name: homeassistant
    network_mode: host
    environment:
      - TZ=America/Edmonton
    volumes:
      - ./config:/config
      - ../ha-daily-temperature-wave/custom_components:/config/custom_components
    restart: unless-stopped
```

```bash
docker compose up -d
```

Open `http://localhost:8123`, finish onboarding, then go to **Settings →
Devices & Services → Add Integration** and search for "Daily Temperature
Wave". After changing the code, restart the container
(`docker compose restart`).

### Python virtual environment (Linux, macOS or WSL)

```bash
uv venv ha-dev && source ha-dev/bin/activate
uv pip install homeassistant
mkdir -p config/custom_components
ln -s "$PWD/custom_components/daily_temperature_wave" config/custom_components/
hass -c config
```

### Debug logging

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.daily_temperature_wave: debug
```

## Releasing

1. Update the version in `custom_components/daily_temperature_wave/manifest.json`
   and add a `:release:` line to `CHANGELOG.rst`.
2. Commit as `[release] x.y.z`, tag it `vx.y.z` (annotated) and push the tag.
3. Create a GitHub release from the tag. HACS offers GitHub releases to users,
   so a tag alone is not enough.
