"""Constants for HRA Recycling."""
from datetime import timedelta
from logging import Logger, getLogger

DOMAIN = "hra_recycling"
NAME = "HRA Recycling"
MANUFACTURER = "HRA"
VERSION = "0.7.0"
ATTRIBUTION = "Data provided by api.hra.no"

LOGGER: Logger = getLogger(__package__)
SCAN_INTERVAL = timedelta(hours=6)
RETRY_INTERVAL = timedelta(minutes=30)

CONF_ADDRESS = "address"
CONF_ENABLE_CALENDAR = "enable_calendar"
CONF_TRACKED_FRACTIONS = "tracked_fractions"
CONF_WEEKS = "weeks"

DEFAULT_WEEKS = 12
MIN_WEEKS = 1
MAX_WEEKS = 52

# Waste type -> translation key. Icons live in icons.json.
WASTE_TYPES = {
    "Restavfall": "restavfall",
    "Matavfall": "matavfall",
    "Papir, papp og kartong": "papir_papp_kartong",
    "Plastemballasje": "plastemballasje",
    "Glass- og metallemballasje": "glass_metall",
}
DEFAULT_ICON = "mdi:trash-can"
