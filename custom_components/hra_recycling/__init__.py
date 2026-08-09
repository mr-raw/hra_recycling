"""HRA Recycling integration."""
from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_ADDRESS
from .coordinator import HraConfigEntry, HraCoordinator
from .hra_api import HraApiClient
from .options import configured_weeks

PLATFORMS = [Platform.SENSOR, Platform.CALENDAR]


async def async_setup_entry(hass: HomeAssistant, entry: HraConfigEntry) -> bool:
    """Set up HRA Recycling from config entry."""
    client = HraApiClient(
        hass, entry.data[CONF_ADDRESS], weeks=configured_weeks(entry)
    )
    coordinator = HraCoordinator(hass, entry, client)

    # Raises ConfigEntryNotReady itself when the first refresh fails.
    await coordinator.async_config_entry_first_refresh()

    # Entries created before 0.5.0 have no unique ID; adopt the agreement ID so
    # duplicate-address setups can be aborted from now on.
    if entry.unique_id is None and client.agreement_id:
        hass.config_entries.async_update_entry(entry, unique_id=client.agreement_id)

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_reload_entry(hass: HomeAssistant, entry: HraConfigEntry) -> None:
    """Reload the entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: HraConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
