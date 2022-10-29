"""Constants for integration_blueprint."""
# Base component constants
NAME = "HRA Recycling"
DOMAIN = "hra_recycling"
DOMAIN_DATA = f"{DOMAIN}_data"
COMPANY = "Raw Software"
VERSION = "0.0.1"
ATTRIBUTION = "Data scraped from https://hra.no/"
ISSUE_URL = "https://github.com/custom-components/hra_recycling/issues"

# Icons
ICON = "mdi:trash-can"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [SENSOR]

# Configuration and options
CONF_ADDRESS = "address"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
