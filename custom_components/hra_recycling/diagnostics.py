"""Diagnostics support for HRA Recycling."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_ADDRESS
from .coordinator import HraConfigEntry

# The address and agreement ID identify a household.
TO_REDACT = {CONF_ADDRESS, "agreement_id", "title", "unique_id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: HraConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    return async_redact_data(
        {
            "entry": {
                "title": entry.title,
                "data": dict(entry.data),
                "options": dict(entry.options),
                "unique_id": entry.unique_id,
            },
            "agreement_id": coordinator.client.agreement_id,
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "schedule": {
                waste_type: [dt.date().isoformat() for dt in dates]
                for waste_type, dates in (coordinator.data or {}).items()
            },
        },
        TO_REDACT,
    )
