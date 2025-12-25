"""
Visualization component for the Daily Temperature Wave.

This module provides SVG generation for the temperature curve visualization.
"""

import math
from typing import Any, Dict

from .constants import (
    VISUAL_BACKGROUND,
    VISUAL_COLOR,
    VISUAL_CURRENT_COLOR,
    VISUAL_HEIGHT,
    VISUAL_PADDING,
    VISUAL_WIDTH,
)


def generate_svg_visualization(visual_data: Dict[str, Any]) -> str:
    """
    Generate SVG visualization from visual data.

    Args:
        visual_data: Visualization data from sensor

    Returns:
        SVG string
    """
    # Extract data
    points = visual_data.get("points", [])
    current_position = visual_data.get("current_position", {})
    solar_noon = visual_data.get("solar_noon", {})
    temp_range = visual_data.get("temperature_range", {})

    # Calculate dimensions
    width = VISUAL_WIDTH
    height = VISUAL_HEIGHT
    padding = VISUAL_PADDING

    # Create SVG path for the curve
    path_points = []
    for point in points:
        x = point["x"]
        y = point["y"]
        path_points.append(f"{x},{y}")

    path_data = "M" + " L".join(path_points)

    # Create SVG
    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="{VISUAL_BACKGROUND}" />
    
    <!-- Temperature curve -->
    <path d="{path_data}" stroke="{VISUAL_COLOR}" stroke-width="2" fill="none" />
    
    <!-- Current position marker -->
    <circle cx="{current_position.get('x', 0)}" cy="{current_position.get('y', 0)}" r="6" fill="{VISUAL_CURRENT_COLOR}" />
    <text x="{current_position.get('x', 0)}" y="{current_position.get('y', 0) - 10}" text-anchor="middle" font-size="12" fill="{VISUAL_CURRENT_COLOR}">
        {current_position.get('temp', '?')}°
    </text>
    
    <!-- Solar noon marker -->
    <line x1="{solar_noon.get('hour', 12) * 10}" y1="{padding}" x2="{solar_noon.get('hour', 12) * 10}" y2="{height - padding}" 
          stroke="#7f8c8d" stroke-width="1" stroke-dasharray="5,5" />
    <text x="{solar_noon.get('hour', 12) * 10}" y="{height - 5}" text-anchor="middle" font-size="10" fill="#7f8c8d">
        Noon
    </text>
    
    <!-- Temperature labels -->
    <text x="{padding}" y="{padding + 15}" font-size="12" fill="#2c3e50">
        {temp_range.get('max', '?')}°{temp_range.get('unit', 'C')}
    </text>
    <text x="{padding}" y="{height - padding}" font-size="12" fill="#2c3e50">
        {temp_range.get('min', '?')}°{temp_range.get('unit', 'C')}
    </text>
    
    <!-- Time markers -->
    <text x="{width - padding}" y="{height - padding}" text-anchor="end" font-size="10" fill="#7f8c8d">
        Time →
    </text>
    </svg>"""

    return svg


def generate_simple_visualization(visual_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a simple JSON visualization for Lovelace cards.

    Args:
        visual_data: Visualization data from sensor

    Returns:
        Simplified visualization data
    """
    return {
        "current_temp": visual_data.get("current_position", {}).get("temp", "?"),
        "current_hours_from_noon": visual_data.get("current_position", {}).get(
            "hours_from_noon", 0
        ),
        "solar_noon": f"{visual_data.get('solar_noon', {}).get('hour', 12):02d}:{visual_data.get('solar_noon', {}).get('minute', 0):02d}",
        "min_temp": visual_data.get("temperature_range", {}).get("min", "?"),
        "max_temp": visual_data.get("temperature_range", {}).get("max", "?"),
        "unit": visual_data.get("temperature_range", {}).get("unit", "C"),
        "is_rising": visual_data.get("current_position", {}).get("hours_from_noon", 0)
        < 0,
    }
