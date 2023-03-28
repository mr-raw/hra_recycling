"""coordinator.py"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.exceptions import ConfigEntryAuthFailed
from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .hra_api import ApiClient, ApiClientError, ApiClientAuthenticationError


class HraDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry = ConfigEntry

    def __init__(self, hass: HomeAssistant, client: ApiClient) -> None:
        """Initialize."""
        self.client = client

        super().__init__(
            hass=hass, logger=LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # We should run a test here to check if the agreement id has been fetched.
            if not self.client.agreement_id:
                await self.client.async_verify_address()
            return await self.client.async_retrieve_fraction_data()
        except ApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except ApiClientError as exception:
            raise UpdateFailed(exception) from exception
