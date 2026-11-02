# Copyright (c) 2025 William Minchin
"""Image entity: a chart of today's wave, for the built-in Picture Entity card."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .chart import render_svg
from .constants import IMAGE_CHART
from .coordinator import (
    DailyTemperatureWaveConfigEntry,
    DailyTemperatureWaveCoordinator,
)
from .entity import DailyTemperatureWaveEntity
from .wave import interval_start

PARALLEL_UPDATES = 0

# How often the chart is redrawn. The "now" marker moves about a pixel every
# five minutes, so redrawing every minute would only make dashboards reload
# the image (and the recorder store a new state) for nothing.
REDRAW_MINUTES = 5


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DailyTemperatureWaveConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the chart for a config entry."""
    async_add_entities([DailyTemperatureWaveChart(entry.runtime_data, IMAGE_CHART)])


class DailyTemperatureWaveChart(DailyTemperatureWaveEntity, ImageEntity):
    """Today's wave, its steps, solar noon and now, as an SVG image.

    The state is when the chart was last redrawn. The ``points`` attribute is
    today's curve, for charting it yourself (e.g. with ApexCharts).
    """

    _attr_content_type = "image/svg+xml"
    # the curve changes every day; keep it out of history
    _unrecorded_attributes = frozenset({"points"})

    def __init__(self, coordinator: DailyTemperatureWaveCoordinator, key: str) -> None:
        """Name the entity after ``key`` and stamp the first drawing."""
        DailyTemperatureWaveEntity.__init__(self, coordinator, key)
        ImageEntity.__init__(self, coordinator.hass)
        self._attr_image_last_updated = self._redraw_slot()

    def _redraw_slot(self) -> datetime:
        return interval_start(self.coordinator.data.now, REDRAW_MINUTES)

    @callback
    def _handle_coordinator_update(self) -> None:
        slot = self._redraw_slot()
        if slot != self._attr_image_last_updated:
            # a new timestamp is what tells dashboards to fetch the image again
            self._attr_image_last_updated = slot
            super()._handle_coordinator_update()

    async def async_image(self) -> bytes:
        """The chart, drawn from the latest calculation."""
        unit = self.hass.config.units.temperature_unit
        return render_svg(
            self.coordinator.data,
            self.display_temperature,
            unit,
            self._second_axis(unit),
        ).encode()

    def _second_axis(self, unit: str) -> tuple | None:
        """The wave's own unit, if it was typed in a different one."""
        entered = self.coordinator.settings.entered_unit
        if f"°{entered}" == unit:
            return None
        if entered == "F":
            return (
                lambda c: c * 9 / 5 + 32,
                lambda f: (f - 32) * 5 / 9,
                "°F",
            )
        return (lambda c: c, lambda c: c, "°C")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Today's curve, midnight to midnight, in the user's unit."""
        return {
            "points": [
                {
                    "datetime": p.moment.isoformat(),
                    "temperature": self.display_temperature(p.temperature),
                }
                for p in self.coordinator.data.curve
            ]
        }
