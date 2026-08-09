"""Constants for HRA Recycling."""
from datetime import timedelta
from logging import Logger, getLogger

DOMAIN = "hra_recycling"
NAME = "HRA Recycling"
MANUFACTURER = "HRA"
VERSION = "0.5.0"
ATTRIBUTION = "Data provided by api.hra.no"

LOGGER: Logger = getLogger(__package__)
SCAN_INTERVAL = timedelta(hours=6)

CONF_ADDRESS = "address"
CONF_ENABLE_CALENDAR = "enable_calendar"

# Waste type configuration: (translation_key, icon, legacy_key)
WASTE_TYPES = {
    "Restavfall": ("restavfall", "mdi:trash-can", "restavfall"),
    "Matavfall": ("matavfall", "mdi:food-apple", "matavfall"),
    "Papir, papp og kartong": ("papir_papp_kartong", "mdi:newspaper", "papir_papp_kartong"),
    "Plastemballasje": ("plastemballasje", "mdi:bottle-soda", "plastemballasje"),
    "Glass- og metallemballasje": ("glass_metall", "mdi:bottle-wine", "glass_metall"),
}
DEFAULT_ICON = "mdi:trash-can"
