"""Data coordinator for HRA Recycling."""
from __future__ import annotations

from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    LOGGER,
    MANUFACTURER,
    NAME,
    RETRY_INTERVAL,
    SCAN_INTERVAL,
    VERSION,
)
from .hra_api import HraApiClient, HraApiError

type HraConfigEntry = ConfigEntry[HraCoordinator]


class HraCoordinator(DataUpdateCoordinator[dict[str, list[datetime]]]):
    """Coordinator to fetch HRA pickup data."""

    config_entry: HraConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: HraConfigEntry, client: HraApiClient
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this coordinator."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.client.agreement_id)},
            name=NAME,
            manufacturer=MANUFACTURER,
            # Explicitly cleared: older versions wrote the integration version
            # here, and the registry keeps fields that stop being set.
            model=None,
            entry_type=DeviceEntryType.SERVICE,
            sw_version=VERSION,
            configuration_url="https://hra.no/tommekalender/",
        )

    async def _async_update_data(self) -> dict[str, list[datetime]]:
        """Fetch data from API."""
        try:
            data = await self.client.async_get_pickup_data()
        except HraApiError as err:
            # Retry sooner than the regular interval; waiting hours after a
            # single blip would leave the schedule needlessly stale.
            self.update_interval = RETRY_INTERVAL
            raise UpdateFailed(str(err)) from err

        self.update_interval = SCAN_INTERVAL
        return data
