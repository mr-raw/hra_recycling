"""Calendar platform for HRA Recycling."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_ENABLE_CALENDAR, DOMAIN
from .coordinator import HraConfigEntry, HraCoordinator
from .entity import HraEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HraConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HRA calendar from config entry."""
    # Options win; fall back to the setup-time value, then to enabled.
    enabled = entry.options.get(
        CONF_ENABLE_CALENDAR, entry.data.get(CONF_ENABLE_CALENDAR, True)
    )
    if not enabled:
        return

    async_add_entities([HraCalendar(entry.runtime_data)])


class HraCalendar(HraEntity, CalendarEntity):
    """Calendar showing all waste pickup dates."""

    _attr_translation_key = "pickup_calendar"

    def __init__(self, coordinator: HraCoordinator) -> None:
        """Initialize calendar."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.client.agreement_id}_calendar"

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
