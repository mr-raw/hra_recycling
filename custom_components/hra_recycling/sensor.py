"""sensor.py"""
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import DOMAIN, LOGGER, NAME, VERSION
from .coordinator import HraDataUpdateCoordinator
from .hra_recycle_entity import HraRecycleEntity
from .hra_api import ApiClientError

FRACTION_NAMES = tuple(
    SensorEntityDescription(
        key=key,
        name=name,
        icon=icon,
    )
    for key, name, icon in (
        ("restavfall", "Restavfall", "mdi:trash-can"),
        ("matavfall", "Matavfall", "mdi:trash-can"),
        ("papir_papp_kartong", "Papir, papp og kartong", "mdi:trash-can"),
        ("plastemballasje", "Plastemballasje", "mdi:trash-can"),
        ("glass_metall", "Glass- og metallemballasje", "mdi:trash-can"),
    )
)


async def async_setup_entry(hass, entry, async_add_entities):
    """This does the setup of the needed HRAREcyclingSensor's"""
    # The coordinator is initialized. The coordinator stores all the information.
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Get the available fractions from the coordinator data
    if coordinator.data is None or not coordinator.data[0].get("sorted_waste"):
        raise ApiClientError("No available fractions found.")

    # Fetch the types of fractions from the json file.
    available_fractions = coordinator.data[0]["sorted_waste"].keys()

    # Create a list of SensorEntityDescriptions for existing fractions
    existing_fraction_names = [
        fraction_name
        for fraction_name in FRACTION_NAMES
        if fraction_name.name in available_fractions
    ]

    # Loop over the list of existing SensorEntityDescriptions and create sensors.
    async_add_entities(
        HRARecyclingSensor(coordinator=coordinator, fraction=fraction_name)
        for fraction_name in existing_fraction_names
    )


class HRARecyclingSensor(HraRecycleEntity, SensorEntity):
    """Sensor representing HRA Recycling fraction."""

    def __init__(
        self,
        coordinator: HraDataUpdateCoordinator,
        fraction: SensorEntityDescription,
    ):
        """Initialize sensor."""
        self._fraction = fraction
        self._agreement_id = coordinator.client.agreement_id
        self._agreement_data = coordinator.client.agreement_data
        self._pickup_data = coordinator.client.pickup_data
        super().__init__(coordinator)

    @property
    def name(self):
        """Return the Friendly name of the sensor."""
        fraction_name = self._fraction.name
        LOGGER.debug("Setting friendly name to %s", fraction_name)
        return fraction_name

    @property
    def unique_id(self):
        key = self._fraction.key
        agreement_id = self._agreement_id
        u_id = f"{DOMAIN}_{key}_{agreement_id}"
        LOGGER.debug("Setting unique_id to %s", u_id)
        return u_id

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return (
            self.coordinator.data[0]
            .get("sorted_waste", {})
            .get(self._fraction.name, [None])[0]
            .date()
            if self.coordinator.data
            else None
        )

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._agreement_id)},
            "name": NAME,
            "manufacturer": NAME,
            "model": f"{DOMAIN} {VERSION}",
            "version": VERSION,
        }

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "date"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._fraction.icon

    @property
    def extra_state_attributes(self):
        if self.coordinator.data is None:
            return
        return {
            "AvtaleId": self.coordinator.client.agreement_data.get("agreementGuid"),
            "Gårdsnr/bruksnr": self.coordinator.client.agreement_data.get(
                "gnrBnrFnrSnr"
            ),
            "Husbokstav": self.coordinator.client.agreement_data.get("houseLetter"),
            "Husnummer": self.coordinator.client.agreement_data.get("houseNumber"),
            "Kommune": self.coordinator.client.agreement_data.get("municipality"),
            "Kommunenr": self.coordinator.client.agreement_data.get(
                "municipalityNumber"
            ),
            "Navn": self.coordinator.client.agreement_data.get("name"),
            "Postnr": self.coordinator.client.agreement_data.get("postalNumber"),
            "Poststed": self.coordinator.client.agreement_data.get("postalPlace"),
            "EiendomsID": self.coordinator.client.agreement_data.get("propertyGuid"),
            "Eiendomsnavn": self.coordinator.client.agreement_data.get("propertyName"),
            "Gatenavn": self.coordinator.client.agreement_data.get("streetName"),
            "Gatenummer": self.coordinator.client.agreement_data.get("streetNumber"),
        }
