"""sensor.py"""
from datetime import datetime, timedelta
import json

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .coordinator import HraDataUpdateCoordinator
from .const import DOMAIN, NAME, VERSION
from .hra_recycle_entity import HraRecycleEntity


async def async_setup_entry(hass, entry, async_add_entities):
    """This is the async setup method"""
    # The coordinator is initialized. The coordinator stores all the information.
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Get the existing fraction names from the coordinator.
    existing_fraction_names = coordinator.get_existing_fraction_names()

    # Loop over the list of existing SensorEntityDescriptions and create sensors.
    entities = [
        HRARecyclingSensor(coordinator=coordinator, fraction=fraction_name)
        for fraction_name in existing_fraction_names
    ]

    # Add the garbage pickup date sensor.
    entities.append(HRAGarbagePickupDateSensor(coordinator=coordinator))
    # Add the days until garbage pickup sensor.
    entities.append(HRADaysUntilGarbagePickupSensor(coordinator=coordinator))
    # Add the fractions on first pickup sensor. Returns a comma separated list of fractions.
    entities.append(HRAFractionsOnFirstPickupSensor(coordinator=coordinator))

    # Add the sensors to the platform.
    async_add_entities(entities)


class HRARecyclingSensor(HraRecycleEntity, SensorEntity):
    """Sensor representing HRA Recycling fraction."""

    def __init__(
        self,
        coordinator: HraDataUpdateCoordinator,
        fraction: SensorEntityDescription,
    ):
        """Initialize sensor."""
        super().__init__(coordinator)
        self._fraction = fraction
        self._agreement_id = coordinator.client.agreement_id
        self._agreement_data = coordinator.client.agreement_data
        self._unique_id = f"{DOMAIN}_{fraction.key}_{coordinator.client.agreement_id}"
        # self._pickup_data = coordinator.client.pickup_data

    @property
    def name(self):
        """Return the Friendly name of the sensor."""
        return self._fraction.name

    @property
    def unique_id(self):
        """The unique id"""
        return self._unique_id

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        sorted_waste = self.coordinator.data.get("sorted_waste", {}).get(
            "sorted_waste", {}
        )
        date_value = sorted_waste.get(self._fraction.name, [None])[0]
        if date_value is not None:
            return date_value.date()

        return None

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._agreement_id)},
            "name": NAME,
            "manufacturer": NAME,
            "model": f"{DOMAIN} {VERSION}",
        }

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "date"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._fraction.icon


class HRAGarbagePickupDateSensor(HraRecycleEntity, SensorEntity):
    """Sensor representing HRA Recycling garbage pickup date."""

    @property
    def name(self):
        """Return the Friendly name of the sensor."""
        return "Førstkommende hentedato"

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_garbage_pickup_date"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data.get("first_pickup_date")

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return "date"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.client.agreement_id)},
            "name": NAME,
            "manufacturer": NAME,
            "model": f"{DOMAIN} {VERSION}",
        }


class HRADaysUntilGarbagePickupSensor(HraRecycleEntity, SensorEntity):
    """Sensor representing days until HRA Recycling garbage pickup date."""

    @property
    def name(self):
        """Return the Friendly name of the sensor."""
        return "Tid fram til neste avfallshenting"

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_time_until_garbage_pickup_date"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        first_pickup_date = self.coordinator.data.get("first_pickup_date")
        if first_pickup_date:
            # Set the time to 09:00 on the pickup date
            target_datetime = datetime.combine(
                first_pickup_date, datetime.min.time()
            ) + timedelta(hours=9)
            # Calculate the difference between the current date/time and the target date/time
            delta = target_datetime - datetime.now()

            # Break down the difference into days, hours, and minutes
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            # Return a string representation of the time difference
            return f"{days} dager, {hours} timer, {minutes} minutter"
        return None

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.client.agreement_id)},
            "name": NAME,
            "manufacturer": NAME,
            "model": f"{DOMAIN} {VERSION}",
        }

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:calendar-clock"


class HRAFractionsOnFirstPickupSensor(HraRecycleEntity, SensorEntity):
    """Sensor representing fractions picked up on HRA Recycling garbage pickup date."""

    @property
    def name(self):
        """Return the Friendly name of the sensor."""
        return "Fraksjoner som hentes på første hentedag"

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_fractions_on_first_pickup_date"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        # Getting the first pickup date from the coordinator's data
        first_pickup_date = self.coordinator.data["first_pickup_date"]

        # Getting the sorted waste data from the coordinator's data
        sorted_waste = self.coordinator.data["sorted_waste"]["sorted_waste"]

        # List to store the names of fractions that match the first pickup date
        fractions = []

        # Iterate through the sorted waste data and check for dates that match the first pickup date
        for fraction_name, dates in sorted_waste.items():
            if any(date.date() == first_pickup_date for date in dates):
                fractions.append(fraction_name)

        # Convert the list of fractions to a JSON string
        fractions_json = json.dumps(fractions)

        # Return the JSON string as the native value
        return fractions_json

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.client.agreement_id)},
            "name": NAME,
            "manufacturer": NAME,
            "model": f"{DOMAIN} {VERSION}",
        }

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:recycle"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "first_pickup_date": self.coordinator.data.get("first_pickup_date"),
        }

    # Maybe move these attributes to separate sensors ??
    # @property
    # def extra_state_attributes(self):
    # """Extra State Attributes"""
    # if self.coordinator.data is None:
    #     return
    # return {
    #     "AvtaleId": self.coordinator.client.agreement_data.get("agreementGuid"),
    #     "Gårdsnr/bruksnr": self.coordinator.client.agreement_data.get(
    #         "gnrBnrFnrSnr"
    #     ),
    #     "Husbokstav": self.coordinator.client.agreement_data.get("houseLetter"),
    #     "Husnummer": self.coordinator.client.agreement_data.get("houseNumber"),
    #     "Kommune": self.coordinator.client.agreement_data.get("municipality"),
    #     "Kommunenr": self.coordinator.client.agreement_data.get(
    #         "municipalityNumber"
    #     ),
    #     "Navn": self.coordinator.client.agreement_data.get("name"),
    #     "Postnr": self.coordinator.client.agreement_data.get("postalNumber"),
    #     "Poststed": self.coordinator.client.agreement_data.get("postalPlace"),
    #     "EiendomsID": self.coordinator.client.agreement_data.get("propertyGuid"),
    #     "Eiendomsnavn": self.coordinator.client.agreement_data.get("propertyName"),
    #     "Gatenavn": self.coordinator.client.agreement_data.get("streetName"),
    #     "Gatenummer": self.coordinator.client.agreement_data.get("streetNumber"),
    # }
