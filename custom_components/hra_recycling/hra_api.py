"""hra_api.py"""
from collections import defaultdict
from datetime import datetime
import asyncio
import socket
import aiohttp
import async_timeout
import httpx
from bs4 import BeautifulSoup
from .const import LOGGER


# https://api.hra.no//search/address?query=R%C3%A5dhusvegen%2039,%202770%20JAREN

TIMEOUT = 10
HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class ApiClientError(Exception):
    """Exception to indicate a general API error."""


class ApiClientCommunicationError(ApiClientError):
    """Exception to indicate a communication error."""


class ApiClientAuthenticationError(ApiClientError):
    """Exception to indicate an authentication error."""


class ApiClient:
    """ApiClient()"""

    def __init__(self, address: str, session: aiohttp.ClientSession) -> None:
        """HRA API Client"""
        self.address = address
        self._session = session
        self.agreement_id: str = ""
        self.agreement_data: dict = {}
        self.pickup_data: dict = {}

    async def async_verify_address(self) -> str:
        """Verify that the provided address is valid."""
        url = f"https://api.hra.no/search/address?query={self.address}"
        data = await self._get_agreement_id_from_address(url)
        self.agreement_data = data[0]
        self.agreement_id = data[0]["agreementGuid"]
        self.address = data[0]["name"]
        return data

    async def _get_agreement_id_from_address(self, url: str) -> str:
        """Get information from the API."""

        try:
            async with async_timeout.timeout(TIMEOUT):
                resp = await self._session.get(url)

            if resp.status == 401:
                raise ApiClientAuthenticationError("Authentication error")
            return await resp.json()

        except asyncio.TimeoutError as exception:
            LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )

        except (aiohttp.ClientError, socket.gaierror) as exception:
            LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.error("Something really wrong happened! - %s", exception)

    async def async_retrieve_fraction_data(self):
        """Get fraction data"""
        data = await self._get_fraction_data(self.agreement_id)
        self.pickup_data = data
        return data

    async def _get_fraction_data(self, uid: str):
        """Actually retrieve data using the uid provied"""
        address = self.address
        uid = self.agreement_id  # We need to add error handling here
        url = f"https://hra.no/tommekalender/?query={address}&agreement={uid}"
        html_doc = await self.download_html_file(url)
        processed_data = await self.process_html_code(html_doc)
        return [processed_data]

    async def download_html_file(self, url: str) -> str:
        """
        Fetches the HTML of a given URL using an async httpx client.
        Raises an error if the response is not valid.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    async def process_html_code(self, html_code: str) -> dict:
        """Process the HTML into json"""
        soup = BeautifulSoup(html_code, "html.parser")
        address = soup.find("h3").text

        garbage_retrieval_rows = soup.find_all(class_="garbage-retrieval-row")

        waste_types_data = defaultdict(list)

        norwegian_weekdays = {
            "Mandag": "Monday",
            "Tirsdag": "Tuesday",
            "Onsdag": "Wednesday",
            "Torsdag": "Thursday",
            "Fredag": "Friday",
            "Lørdag": "Saturday",
            "Søndag": "Sunday",
        }

        norwegian_months = {
            "jan": "Jan",
            "feb": "Feb",
            "mar": "Mar",
            "apr": "Apr",
            "mai": "May",
            "jun": "Jun",
            "jul": "Jul",
            "aug": "Aug",
            "sep": "Sep",
            "okt": "Oct",
            "nov": "Nov",
            "des": "Dec",
        }

        date_format = "%A %d. %b"
        today = datetime.now()

        for row in garbage_retrieval_rows:
            day_date = row.find(class_="text-center").get_text(
                separator=" ", strip=True
            )

            for norwegian_day, english_day in norwegian_weekdays.items():
                day_date = day_date.replace(norwegian_day, english_day)

            for norwegian_month, english_month in norwegian_months.items():
                day_date = day_date.replace(norwegian_month, english_month)

            date_object = datetime.strptime(day_date, date_format)
            date_object = date_object.replace(year=today.year)

            if date_object < today:
                date_object = date_object.replace(year=today.year + 1)

            types = row.find_all(class_=["col-6", "col-md-2"])

            for waste_type in types:
                waste_name_div = waste_type.find("div")
                if waste_name_div:
                    waste_name = waste_name_div.text
                    waste_types_data[waste_name].append(date_object)

        sorted_waste_types_data = dict(sorted(waste_types_data.items()))

        return {
            "agreementGuid": self.agreement_id,
            "address": address,
            "sorted_waste": sorted_waste_types_data,
        }
