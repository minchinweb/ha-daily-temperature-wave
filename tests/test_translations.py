# Copyright (c) 2025 William Minchin
"""`translations/en.json` must match `strings.json`.

Home Assistant only reads `translations/` for custom integrations, and doesn't
resolve `[%key:...%]` references there, so `en.json` is `strings.json` with
the references filled in. Regenerate it with `python tests/test_translations.py`.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

COMPONENT = (
    Path(__file__).parent.parent / "custom_components" / "daily_temperature_wave"
)
STRINGS = COMPONENT / "strings.json"
EN = COMPONENT / "translations" / "en.json"
_REFERENCE = re.compile(r"\[%key:component::daily_temperature_wave::(.+)%\]")


def resolve(strings: dict[str, Any]) -> dict[str, Any]:
    """Fill in this integration's own ``[%key:...%]`` references."""

    def lookup(path: str) -> Any:
        node: Any = strings
        for part in path.split("::"):
            node = node[part]
        return node

    def walk(node: Any) -> Any:
        if isinstance(node, dict):
            return {key: walk(value) for key, value in node.items()}
        if match := _REFERENCE.fullmatch(node):
            return walk(lookup(match[1]))
        return node

    return walk(strings)


def test_en_matches_strings():
    strings = json.loads(STRINGS.read_text(encoding="utf-8"))
    assert json.loads(EN.read_text(encoding="utf-8")) == resolve(strings)


def test_every_entity_has_a_name():
    from custom_components.daily_temperature_wave.sensor import SENSORS

    entity = json.loads(EN.read_text(encoding="utf-8"))["entity"]
    for description in SENSORS:
        assert entity["sensor"][description.translation_key]["name"]
    assert entity["binary_sensor"]["rising"]["name"]


if __name__ == "__main__":
    EN.write_text(
        json.dumps(
            resolve(json.loads(STRINGS.read_text(encoding="utf-8"))),
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
