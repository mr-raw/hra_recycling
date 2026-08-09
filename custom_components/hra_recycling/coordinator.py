"""Data coordinator for HRA Recycling."""
from __future__ import annotations

from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, MANUFACTURER, NAME, SCAN_INTERVAL, VERSION
from .hra_api import HraApiClient, HraApiError


class HraCoordinator(DataUpdateCoordinator[dict[str, list[datetime]]]):
    """Coordinator to fetch HRA pickup data."""

    def __init__(self, hass: HomeAssistant, client: HraApiClient) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
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
            model=VERSION,
            configuration_url="https://hra.no/tommekalender/",
        )

    async def _async_update_data(self) -> dict[str, list[datetime]]:
        """Fetch data from API."""
        try:
            return await self.client.async_get_pickup_data()
        except HraApiError as err:
            raise UpdateFailed(str(err)) from err
