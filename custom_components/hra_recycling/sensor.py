"""sensor.py"""
from homeassistant.components.sensor import SensorEntityDescription, SensorEntity
from .const import DOMAIN, LOGGER
from .coordinator import HraDataUpdateCoordinator
from .HRA_Recycle_Entity import HRA_Recycle_Entity

FRACTION_NAMES = (
    SensorEntityDescription(
        key="restavfall",
        name="Restavfall",
        icon="mdi:trash-can",
    ),
    SensorEntityDescription(
        key="matavfall",
        name="Matavfall",
        icon="mdi:trash-can",
    ),
    SensorEntityDescription(
        key="papir_papp_kartong",
        name="Papir, papp og kartong",
        icon="mdi:trash-can",
    ),
    SensorEntityDescription(
        key="plastemballasje",
        name="Plastemballasje",
        icon="mdi:trash-can",
    ),
    SensorEntityDescription(
        key="glass_metall",
        name="Glass- og metallemballasje",
        icon="mdi:trash-can",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """async_setup_entry"""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    # Loop over the list of SensorEntityDescription's and create sensors.
    async_add_entities(
        HRARecyclingSensor(coordinator=coordinator, fraction=fraction_name)
        for fraction_name in FRACTION_NAMES
    )


class HRARecyclingSensor(HRA_Recycle_Entity, SensorEntity):
    """Sensor representing HRA Recycling fraction."""

    def __init__(
        self,
        coordinator: HraDataUpdateCoordinator,
        fraction: SensorEntityDescription,
    ):
        """Initialize sensor."""
        self.fraction = fraction
        self.agreement_id = coordinator.data[0].get("agreementGuid")
        super().__init__(coordinator)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.fraction.name

    @property
    def unique_id(self):
        """Return a unique ID."""
        key = self.fraction.key
        addr_fixed = self.coordinator.client.address.lower().replace(" ", "_")
        u_id = f"{DOMAIN}_{key}_{addr_fixed}"
        LOGGER.debug(u_id)
        return u_id

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return "2023-03-26"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.agreement_id)},
            "name": "HRA Recycling",
            "manufacturer": "HRA",
            "model": "Recycling",
        }

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self.fraction.icon

    @property
    def extra_state_attributes(self):
        return {
            "AvtaleId": self.coordinator.data[0].get("agreementGuid"),
            "Gårdsnr/bruksnr": self.coordinator.data[0].get("gnrBnrFnrSnr"),
            "Husbokstav": self.coordinator.data[0].get("houseLetter"),
            "Husnummer": self.coordinator.data[0].get("houseNumber"),
            "Kommune": self.coordinator.data[0].get("municipality"),
            "Kommunenr": self.coordinator.data[0].get("municipalityNumber"),
            "Navn": self.coordinator.data[0].get("name"),
            "Postnr": self.coordinator.data[0].get("postalNumber"),
            "Poststed": self.coordinator.data[0].get("postalPlace"),
            "EiendomsID": self.coordinator.data[0].get("propertyGuid"),
            "Eiendomsnavn": self.coordinator.data[0].get("propertyName"),
            "Gatenavn": self.coordinator.data[0].get("streetName"),
            "Gatenummer": self.coordinator.data[0].get("streetNumber"),
        }

    async def async_update(self):
        """Update the sensor data."""
        await self.coordinator.async_request_refresh()
