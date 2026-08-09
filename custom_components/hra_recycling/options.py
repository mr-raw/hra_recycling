"""Option accessors for HRA Recycling.

Options win, then the value stored at setup time, then the default. Entries
created before options existed keep working through the data fallback.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .const import (
    CONF_ENABLE_CALENDAR,
    CONF_TRACKED_FRACTIONS,
    CONF_WEEKS,
    DEFAULT_WEEKS,
)
from .coordinator import HraConfigEntry


def _get(entry: HraConfigEntry, key: str, default: Any) -> Any:
    """Return an option, falling back to entry data and then the default."""
    return entry.options.get(key, entry.data.get(key, default))


def calendar_enabled(entry: HraConfigEntry) -> bool:
    """Return whether the pickup calendar should exist."""
    return bool(_get(entry, CONF_ENABLE_CALENDAR, True))


def configured_weeks(entry: HraConfigEntry) -> int:
    """Return how many weeks of pickups to fetch."""
    return int(_get(entry, CONF_WEEKS, DEFAULT_WEEKS))


def tracked_fractions(entry: HraConfigEntry, available: Iterable[str]) -> set[str]:
    """Return the fractions to expose, defaulting to all available ones."""
    available = set(available)
    selected = _get(entry, CONF_TRACKED_FRACTIONS, None)
    if not selected:
        return available
    # Drop selections the address no longer has a schedule for.
    return set(selected) & available
