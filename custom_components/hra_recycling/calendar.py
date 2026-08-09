"""Calendar platform for HRA Recycling."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, WASTE_TYPES
from .coordinator import HraConfigEntry, HraCoordinator
from .entity import HraEntity
from .options import calendar_enabled, tracked_fractions

PARALLEL_UPDATES = 0


def _unique_id(coordinator: HraCoordinator) -> str:
    """Return the calendar's unique ID."""
    return f"{DOMAIN}_{coordinator.client.agreement_id}_calendar"


@callback
def _async_remove_calendar(
    hass: HomeAssistant, entry: HraConfigEntry, coordinator: HraCoordinator
) -> None:
    """Remove a calendar left behind after it was switched off."""
    registry = er.async_get(hass)
    if entity_id := registry.async_get_entity_id(
        Platform.CALENDAR, DOMAIN, _unique_id(coordinator)
    ):
        registry.async_remove(entity_id)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HraConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HRA calendar from config entry."""
    coordinator = entry.runtime_data

    if not calendar_enabled(entry):
        _async_remove_calendar(hass, entry, coordinator)
        return

    tracked = tracked_fractions(entry, set(WASTE_TYPES) | set(coordinator.data or {}))
    async_add_entities([HraCalendar(coordinator, tracked)])


class HraCalendar(HraEntity, CalendarEntity):
    """Calendar showing all waste pickup dates."""

    _attr_translation_key = "pickup_calendar"

    def __init__(self, coordinator: HraCoordinator, tracked: set[str]) -> None:
        """Initialize calendar."""
        super().__init__(coordinator)
        self._tracked = tracked
        self._attr_unique_id = _unique_id(coordinator)

    def _schedule(self) -> dict[str, list[datetime]]:
        """Return the schedule limited to the tracked fractions."""
        return {
            waste_type: dates
            for waste_type, dates in (self.coordinator.data or {}).items()
            if waste_type in self._tracked
        }

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        today = dt_util.now().date()
        next_pickup: tuple[str, datetime] | None = None

        for waste_type, dates in self._schedule().items():
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
        events: list[CalendarEvent] = []
        start = start_date.date()
        end = end_date.date()

        for waste_type, dates in self._schedule().items():
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
