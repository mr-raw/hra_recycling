"""HRA API Client"""
import logging
import asyncio
import socket
import aiohttp
import async_timeout

# https://api.hra.no//search/address?query=R%C3%A5dhusvegen%2039,%202770%20JAREN

TIMEOUT = 10
_LOGGER: logging.Logger = logging.getLogger(__package__)
HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class ApiClient:
    """ApiClient()"""

    def __init__(self, address: str, session: aiohttp.ClientSession) -> None:
        """HRA API Client"""
        self._address = address  # This your street address
        self._session = session
        self._agreement_id = ""

    async def async_get_data(self) -> list:
        """Get the agreementID from from api.hra.no."""

        # if the _agreement_id = "", then fetch the agreement id. Then fetch the collection data
        # if the _agreement_id = <correc_id>, then go ahead and fetch the collection data
        url = "https://api.hra.no/search/address?query=R%C3%A5dhusvegen%2039%2C%202770%20JAREN"

        if self._agreement_id == "":
            temp = await self.return_agreement_id_from_address(url)
            self._agreement_id = temp[0]
        return await self.return_agreement_id_from_address(url)

    async def return_agreement_id_from_address(self, url: str) -> list:
        """Get information from the API."""

        try:
            async with async_timeout.timeout(TIMEOUT):
                resp = await self._session.get(url)
            return await resp.json()

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )

        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
