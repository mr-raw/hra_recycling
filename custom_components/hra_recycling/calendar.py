"""Calendar platform for HRA Recycling."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import ATTRIBUTION, CONF_ENABLE_CALENDAR, DOMAIN
from .coordinator import HraCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HRA calendar from config entry."""
    # Options win; fall back to the setup-time value, then to enabled.
    enabled = entry.options.get(
        CONF_ENABLE_CALENDAR, entry.data.get(CONF_ENABLE_CALENDAR, True)
    )
    if not enabled:
        return

    coordinator: HraCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HraCalendar(coordinator)])


class HraCalendar(CoordinatorEntity[HraCoordinator], CalendarEntity):
    """Calendar showing all waste pickup dates."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _attr_translation_key = "pickup_calendar"

    def __init__(self, coordinator: HraCoordinator) -> None:
        """Initialize calendar."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.client.agreement_id}_calendar"
        self._attr_device_info = coordinator.device_info

    async def async_added_to_hass(self) -> None:
        """Refresh at midnight so the next event rolls over on time."""
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
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        if not self.coordinator.data:
            return None

        today = dt_util.now().date()
        next_pickup: tuple[str, datetime] | None = None

        for waste_type, dates in self.coordinator.data.items():
            for dt in dates:
                pickup_date = dt.date()
                if pickup_date >= today:
                    if not next_pickup or pickup_date < next_pickup[1].date():
                        next_pickup = (waste_type, dt)
                    break

        if not next_pickup:
            return None

        waste_type, pickup_dt = next_pickup
        pickup_date = pickup_dt.date()
        return CalendarEvent(
            summary=waste_type,
            start=pickup_date,
            end=pickup_date + timedelta(days=1),
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return events in date range."""
        if not self.coordinator.data:
            return []

        events: list[CalendarEvent] = []
        start = start_date.date()
        end = end_date.date()

        for waste_type, dates in self.coordinator.data.items():
            for dt in dates:
                pickup_date = dt.date()
                if start <= pickup_date < end:
                    events.append(
                        CalendarEvent(
                            summary=waste_type,
                            start=pickup_date,
                            end=pickup_date + timedelta(days=1),
                        )
                    )

        return sorted(events, key=lambda e: e.start)
