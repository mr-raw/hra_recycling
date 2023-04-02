"""hra_recycle_entity.py"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import ATTRIBUTION


class HraRecycleEntity(CoordinatorEntity):
    """HraRecycleEntity"""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator):
        super().__init__(coordinator)
        # self._attr_unique_id = coordinator.config_entry.entry_id
        # self._attr_device_info = DeviceInfo(
        #    identifiers={(DOMAIN, self.unique_id)},
        #    name=NAME,
        #    model=VERSION,
        #    manufacturer=NAME,
        # )
