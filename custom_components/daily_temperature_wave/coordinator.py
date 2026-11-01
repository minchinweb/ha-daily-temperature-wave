# Copyright (c) 2025 William Minchin
"""Work out the wave once a minute and share it with every entity."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.sun import get_astral_event_date
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .constants import (
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_SOLAR_NOON_OVERRIDE,
    CONF_STEP_INTERVAL,
    CONF_STEP_RESOLUTION,
    CONF_WAVE_SPREAD,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_STEP_INTERVAL,
    DEFAULT_STEP_RESOLUTION,
    DEFAULT_WAVE_SPREAD,
    DOMAIN,
    FORECAST_DAYS,
)
from .wave import (
    hours_from_noon,
    interval_start,
    is_rising,
    parse_step,
    parse_temperature_celsius,
    round_to_step,
    temperature_at,
)

_LOGGER = logging.getLogger(__name__)

# `astral.sun.noon`
_SUN_EVENT_NOON = "noon"
# Resolution of the curve drawn by the visual sensor.
_CURVE_STEP = timedelta(minutes=30)

type DailyTemperatureWaveConfigEntry = ConfigEntry[DailyTemperatureWaveCoordinator]


def parse_time(value: str | None) -> time | None:
    """Parse ``"HH:MM"`` or ``"HH:MM:SS"``; ``None`` or ``""`` gives ``None``.

    Raises:
        ValueError: If ``value`` isn't a time.
    """
    if not value:
        return None
    return time.fromisoformat(value.strip())


@dataclass(frozen=True)
class WaveSettings:
    """The integration's options, parsed."""

    min_temp: float  # Celsius
    max_temp: float  # Celsius
    spread: float
    step: float  # in `step_unit`
    step_unit: str
    step_interval: int  # minutes
    solar_noon_override: time | None

    @classmethod
    def from_options(cls, options: Mapping[str, Any]) -> WaveSettings:
        """Build from a config entry's data and options (already validated).

        Raises:
            ValueError: If a value can't be parsed.
        """
        step, step_unit = parse_step(
            options.get(CONF_STEP_RESOLUTION, DEFAULT_STEP_RESOLUTION)
        )
        return cls(
            min_temp=parse_temperature_celsius(
                options.get(CONF_MIN_TEMP, DEFAULT_MIN_TEMP)
            ),
            max_temp=parse_temperature_celsius(
                options.get(CONF_MAX_TEMP, DEFAULT_MAX_TEMP)
            ),
            spread=float(options.get(CONF_WAVE_SPREAD, DEFAULT_WAVE_SPREAD)),
            step=step,
            step_unit=step_unit,
            step_interval=int(options.get(CONF_STEP_INTERVAL, DEFAULT_STEP_INTERVAL)),
            solar_noon_override=parse_time(options.get(CONF_SOLAR_NOON_OVERRIDE)),
        )


@dataclass(frozen=True)
class TimedTemperature:
    """A temperature (Celsius) at a moment."""

    moment: datetime
    temperature: float


@dataclass(frozen=True)
class DailyForecast:
    """One day's high and low (Celsius)."""

    day: date
    solar_noon: datetime
    high: float
    low: float


@dataclass(frozen=True)
class WaveState:
    """Everything the entities show, worked out at one moment."""

    now: datetime
    solar_noon: datetime
    hours_from_noon: float
    current: float
    current_step: float
    rising: bool
    # next 24 hours, on the hour
    hourly: list[TimedTemperature]
    # next 24 hours, at the start of each step interval, rounded to the step
    stepped: list[TimedTemperature]
    daily: list[DailyForecast]
    daily_step: list[DailyForecast]
    # today, midnight to midnight, every `_CURVE_STEP`
    curve: list[TimedTemperature]
    # today, midnight to midnight: each step where the stepped temperature
    # changes, i.e. a thermostat schedule
    schedule: list[TimedTemperature]


class DailyTemperatureWaveCoordinator(DataUpdateCoordinator[WaveState]):
    """Recalculates the wave at the top of every minute."""

    config_entry: DailyTemperatureWaveConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: DailyTemperatureWaveConfigEntry
    ) -> None:
        """Read the settings from ``entry``.

        Raises:
            ValueError: If the entry's options can't be parsed.
        """
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            # driven by `async_track_time_change` instead (see `async_start`)
            update_interval=None,
        )
        self.settings = WaveSettings.from_options({**entry.data, **entry.options})
        self._noon_cache: dict[date, datetime] = {}

    @callback
    def async_start(self) -> None:
        """Refresh at the start of every minute, until the entry is unloaded."""
        self.config_entry.async_on_unload(
            async_track_time_change(self.hass, self._async_tick, second=0)
        )

    @callback
    def _async_tick(self, now: datetime) -> None:
        self.async_set_updated_data(self.calculate(dt_util.as_local(now)))

    async def _async_update_data(self) -> WaveState:
        return self.calculate(dt_util.now())

    def solar_noon(self, day: date) -> datetime:
        """Solar noon on ``day``, in Home Assistant's time zone."""
        if (cached := self._noon_cache.get(day)) is not None:
            return cached
        time_zone = dt_util.get_default_time_zone()
        override = self.settings.solar_noon_override
        noon = None
        if override is None:
            noon = get_astral_event_date(self.hass, _SUN_EVENT_NOON, day)
            if noon is None:
                _LOGGER.warning("No solar noon on %s; using 12:00", day)
        if noon is None:
            noon = datetime.combine(day, override or time(12), tzinfo=time_zone)
        noon = noon.astimezone(time_zone)
        if len(self._noon_cache) > FORECAST_DAYS + 2:
            self._noon_cache.clear()
        self._noon_cache[day] = noon
        return noon

    def temperature(self, moment: datetime) -> float:
        """The wave's temperature (Celsius) at ``moment``."""
        hours = hours_from_noon(moment, self.solar_noon(moment.date()))
        settings = self.settings
        return temperature_at(
            hours, settings.min_temp, settings.max_temp, settings.spread
        )

    def stepped_temperature(self, moment: datetime) -> float:
        """The temperature held for the step interval containing ``moment``."""
        start = interval_start(moment, self.settings.step_interval)
        return self._round(self.temperature(start))

    def _round(self, temp: float) -> float:
        return round_to_step(temp, self.settings.step, self.settings.step_unit)

    def calculate(self, now: datetime) -> WaveState:
        """Work out everything the entities need, as of ``now`` (local time)."""
        settings = self.settings
        today = now.date()
        noon = self.solar_noon(today)
        hours = hours_from_noon(now, noon)

        hour_start = now.replace(minute=0, second=0, microsecond=0)
        hourly = [
            TimedTemperature(moment, self.temperature(moment))
            for moment in (hour_start + timedelta(hours=h) for h in range(24))
        ]

        interval = timedelta(minutes=settings.step_interval)
        moment = interval_start(now, settings.step_interval)
        end = now + timedelta(hours=24)
        stepped = []
        while moment < end:
            stepped.append(TimedTemperature(moment, self.stepped_temperature(moment)))
            moment += interval

        days = [today + timedelta(days=d) for d in range(FORECAST_DAYS)]
        daily = [
            DailyForecast(
                day, self.solar_noon(day), settings.max_temp, settings.min_temp
            )
            for day in days
        ]
        daily_step = [
            DailyForecast(f.day, f.solar_noon, self._round(f.high), self._round(f.low))
            for f in daily
        ]

        midnight = datetime.combine(today, time(), tzinfo=now.tzinfo)
        curve_points = int(timedelta(days=1) / _CURVE_STEP) + 1
        curve = [
            TimedTemperature(moment, self.temperature(moment))
            for moment in (midnight + _CURVE_STEP * i for i in range(curve_points))
        ]

        return WaveState(
            now=now,
            solar_noon=noon,
            hours_from_noon=hours,
            current=temperature_at(
                hours, settings.min_temp, settings.max_temp, settings.spread
            ),
            current_step=self.stepped_temperature(now),
            rising=is_rising(hours),
            hourly=hourly,
            stepped=stepped,
            daily=daily,
            daily_step=daily_step,
            curve=curve,
            schedule=self.schedule(midnight),
        )

    def schedule(self, midnight: datetime) -> list[TimedTemperature]:
        """The day from ``midnight``: each step where the temperature changes.

        The first entry is always at midnight. Times are wall-clock, so on a
        daylight saving change the steps still fall on the hour and half hour.
        """
        interval = timedelta(minutes=self.settings.step_interval)
        changes: list[TimedTemperature] = []
        moment = midnight
        while moment.date() == midnight.date():
            temp = self.stepped_temperature(moment)
            if not changes or temp != changes[-1].temperature:
                changes.append(TimedTemperature(moment, temp))
            moment += interval
        return changes
