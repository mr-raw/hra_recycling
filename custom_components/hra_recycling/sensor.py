"""Sensor platform for HRA Recycling."""
from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DEFAULT_ICON, DOMAIN, WASTE_TYPES
from .coordinator import HraConfigEntry, HraCoordinator
from .entity import HraEntity
from .options import tracked_fractions

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


def _unique_id(coordinator: HraCoordinator, key: str) -> str:
    """Return the unique ID for a sensor key."""
    return f"{DOMAIN}_{coordinator.client.agreement_id}_{key}"


@callback
def _async_purge_untracked(
    hass: HomeAssistant,
    entry: HraConfigEntry,
    coordinator: HraCoordinator,
    tracked: set[str],
) -> None:
    """Drop registry entries for fractions the user no longer tracks."""
    registry = er.async_get(hass)
    wanted = {_unique_id(coordinator, _describe(f).key) for f in tracked}

    for registered in er.async_entries_for_config_entry(registry, entry.entry_id):
        if registered.domain == Platform.SENSOR and registered.unique_id not in wanted:
            registry.async_remove(registered.entity_id)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HraConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HRA sensors from config entry."""
    coordinator = entry.runtime_data

    # Always consider the known waste types, even if this refresh returned
    # nothing, so an empty response never silently leaves the integration
    # without entities.
    known = set(WASTE_TYPES)
    added: set[str] = set()

    _async_purge_untracked(
        hass, entry, coordinator, tracked_fractions(entry, known | set(coordinator.data or {}))
    )

    @callback
    def _add_new_waste_types() -> None:
        """Add entities for tracked waste types seen for the first time."""
        tracked = tracked_fractions(entry, known | set(coordinator.data or {}))
        new = tracked - added
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
        self._attr_unique_id = _unique_id(coordinator, description.key)

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
