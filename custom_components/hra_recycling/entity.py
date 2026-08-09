"""Base entity for HRA Recycling."""
from __future__ import annotations

from datetime import datetime

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import HraCoordinator


class HraEntity(CoordinatorEntity[HraCoordinator]):
    """Shared behaviour for every HRA entity."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: HraCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info

    async def async_added_to_hass(self) -> None:
        """Register a midnight refresh so day-relative values stay correct."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_track_time_change(
                self.hass, self._handle_midnight, hour=0, minute=0, second=0
            )
        )

    @callback
    def _handle_midnight(self, now: datetime) -> None:
        """Rewrite the state at the day boundary."""
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True while a schedule is known.

        Pickup dates are fixed weeks ahead, so a failed refresh is no reason to
        hide them - only never having fetched any is.
        """
        return self.coordinator.data is not None
