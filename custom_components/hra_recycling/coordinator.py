"""coordinator.py"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.components.sensor import SensorEntityDescription

from .const import DOMAIN, LOGGER, SCAN_INTERVAL
from .hra_api import HraApiClient, ApiClientNoPickupDataFound, ApiClientError

# FRACTION_NAMES = tuple(
#     SensorEntityDescription(
#         key=key,
#         name=name,
#         icon=icon,
#     )
#     for key, name, icon in (
#         ("restavfall", "Restavfall", "mdi:trash-can"),
#         ("matavfall", "Matavfall", "mdi:trash-can"),
#         ("papir_papp_kartong", "Papir, papp og kartong", "mdi:trash-can"),
#         ("plastemballasje", "Plastemballasje", "mdi:trash-can"),
#         ("glass_metall", "Glass- og metallemballasje", "mdi:trash-can"),
#     )
# )

FRACTION_NAMES = tuple(
    SensorEntityDescription(
        key=key,
        name=name,
        icon=icon,
    )
    for key, name, icon in (
        ("Glass- og metallemballasje", "Glass- og metallemballasje", "mdi:trash-can"),
        ("Matavfall", "Matavfall", "mdi:trash-can"),
        ("Papir, papp og kartong", "Papir, papp og kartong", "mdi:trash-can"),
        ("Plastemballasje", "Plastemballasje", "mdi:trash-can"),
        ("Restavfall", "Restavfall", "mdi:trash-can"),
    )
)


class HraDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry = ConfigEntry

    def __init__(self, hass: HomeAssistant, client: HraApiClient) -> None:
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
            sorted_waste_data = await self.client.async_retrieve_fraction_data()
            sorted_waste = sorted_waste_data["sorted_waste"]

            first_pickup_date = min(
                date for dates in sorted_waste.values() for date in dates
            )

            # Return the data including the first pickup date
            return {
                "first_pickup_date": first_pickup_date.date(),
                "sorted_waste": sorted_waste_data,
            }
        except ApiClientNoPickupDataFound as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except ApiClientError as exception:
            raise UpdateFailed(exception) from exception

    def get_existing_fraction_names(self):
        """Return a list of existing fraction names."""
        if (
            self.data is None
            or not self.data.get("sorted_waste")
            or not self.data["sorted_waste"].get("sorted_waste")
        ):
            raise ApiClientError("No available fractions found.")

        available_fractions = self.data["sorted_waste"]["sorted_waste"].keys()
        existing_fraction_names = [
            fraction_name
            for fraction_name in FRACTION_NAMES
            if fraction_name.key in available_fractions
        ]
        return existing_fraction_names
