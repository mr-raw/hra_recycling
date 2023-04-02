"""const.py"""
from datetime import timedelta
from logging import Logger, getLogger

# Base component constants

NAME = "HRA Recycling"
DOMAIN = "hra_recycling"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.0"
ATTRIBUTION = "Data scraped from https://hra.no/"
ISSUE_URL = "https://github.com/mr-raw/hra_recycling/issues"

LOGGER: Logger = getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=3600)

# Platforms
SENSOR = "sensor"
PLATFORMS = [SENSOR]

# Configuration and options
CONF_ADDRESS = "address"
# CONF_GUID = ""

# Defaults
# DEFAULT_NAME = DOMAIN
