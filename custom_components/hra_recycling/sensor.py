"""Sensor platform for HRA Recycling."""
from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DEFAULT_ICON, DOMAIN, WASTE_TYPES
from .coordinator import HraConfigEntry, HraCoordinator
from .entity import HraEntity

PARALLEL_UPDATES = 0


def _describe(waste_type: str) -> SensorEntityDescription:
    """Build the entity description for a waste type."""
    if translation_key := WASTE_TYPES.get(waste_type):
        return SensorEntityDescription(
            key=translation_key,
            translation_key=translation_key,
            device_class=SensorDeviceClass.DATE,
        )

    # Unknown fraction: no translation exists, so fall back to the API label.
    key = waste_type.lower().replace(" ", "_").replace(",", "").replace("-", "_")
    return SensorEntityDescription(
        key=key,
        name=waste_type,
        icon=DEFAULT_ICON,
        device_class=SensorDeviceClass.DATE,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HraConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HRA sensors from config entry."""
    coordinator = entry.runtime_data

    # Always create the known waste types, even if this refresh returned nothing,
    # so an empty response never silently leaves the integration without entities.
    known = set(WASTE_TYPES)
    added: set[str] = set()

    @callback
    def _add_new_waste_types() -> None:
        """Add entities for waste types seen for the first time."""
        wanted = known | set(coordinator.data or {})
        new = wanted - added
        if not new:
            return
        added.update(new)
        async_add_entities(
            HraSensor(coordinator, waste_type, _describe(waste_type))
            for waste_type in sorted(new)
        )

    _add_new_waste_types()
    entry.async_on_unload(coordinator.async_add_listener(_add_new_waste_types))


class HraSensor(HraEntity, SensorEntity):
    """Sensor for a waste type pickup date."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: HraCoordinator,
        waste_type: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._waste_type = waste_type
        self._attr_unique_id = f"{DOMAIN}_{coordinator.client.agreement_id}_{description.key}"

    @property
    def _next_pickup(self) -> date | None:
        """Return the next pickup date for this waste type."""
        if not self.coordinator.data:
            return None
        dates = self.coordinator.data.get(self._waste_type, [])
        if not dates:
            return None
        return dates[0].date()

    @property
    def native_value(self) -> date | None:
        """Return the next pickup date."""
        return self._next_pickup

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes."""
        pickup = self._next_pickup
        if pickup is None:
            return {}
        return {
            "date": pickup.isoformat(),
            "days_until": (pickup - dt_util.now().date()).days,
        }
