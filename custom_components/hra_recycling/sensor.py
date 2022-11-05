"""Sensor platform for integration_blueprint."""
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN, ICON
from .entity import Entity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([CreateSensor(coordinator, entry)])


class CreateSensor(Entity, SensorEntity):
    """integration_blueprint Sensor class."""

    @property
    def name(self):
        """Return the name of the sensor."""
        # return f"{DEFAULT_NAME}_{SENSOR}"
        return "HRA Recycle Sensor"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data[0].get("propertyName")

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

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
