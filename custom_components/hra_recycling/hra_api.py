"""hra_api.py"""
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict

import httpx
from bs4 import BeautifulSoup

# HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class ApiClientError(Exception):
    """Exception to indicate a general API error."""


class ApiClientCommunicationError(ApiClientError):
    """Exception to indicate a communication error."""


class ApiClientNoPickupDataFound(ApiClientError):
    """Exception to indicate an authentication error."""


class HraApiClient:
    """ApiClient()"""

    def __init__(self, address: str) -> None:
        """HRA API Client"""
        self.address = address
        self.agreement_id: str = ""
        self.agreement_data: dict = {}
        self.pickup_data: dict = {}

    async def async_verify_address(self) -> str:
        """Verify that the provided address is valid."""
        if self.address == "":
            raise ApiClientError("The address field is empty.")
        url = f"https://api.hra.no/search/address?query={self.address}"
        data = await self._get_agreement_id_from_address(url)
        self.address = data[0]["name"]
        self.agreement_id = data[0]["agreementGuid"]
        self.agreement_data = data[0]
        return data

    async def _get_agreement_id_from_address(self, url: str) -> str:
        """Get information from the API."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10)
            except httpx.TimeoutException as esc:
                raise ApiClientCommunicationError("Request timed out") from esc
            if response.status_code == 401:
                raise ApiClientNoPickupDataFound("Authentication error")
            return response.json()

    async def async_retrieve_fraction_data(self) -> Dict[str, Any]:
        """
        Get fraction data and update the pickup_data attribute with the retrieved data.

        Returns:
            data (Dict[str, Any]): The retrieved fraction data.
        """
        self.pickup_data = await self._get_fraction_data()
        return self.pickup_data

    async def _get_fraction_data(self) -> Dict[str, Any]:
        """
        Retrieve fraction data using the instance's address and agreement_id attributes.

        Returns:
            List[Dict[str, Any]]: A list containing the processed data as a dictionary.

        Raises:
            ApiClientError: If the address or agreementID fields are empty.
        """
        if self.address == "":
            raise ApiClientError("The address field is empty.")
        if self.agreement_id == "":
            raise ApiClientError("The agreementID field is empty.")

        url = (
            f"https://hra.no/tommekalender/?"
            f"query={self.address}&"
            f"agreement={self.agreement_id}"
        )
        html_doc = await self.download_html_file(url)
        processed_data = await self.process_html_code(html_doc)
        return processed_data

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
