"""Invoke tasks; run with ``uv run invoke --list``."""

from __future__ import annotations

try:
    from minchin.tasks import (  # noqa: F401
        check,
        format_code,
        lint,
        test,
        update,
        upgrade,
    )
except ImportError:
    print("[WARN] minchin.tasks not installed.")

# No `minchin.releaser`: it bumps a Python `__version__`, but a Home Assistant
# integration's version lives in `manifest.json`. See docs/development.md.
