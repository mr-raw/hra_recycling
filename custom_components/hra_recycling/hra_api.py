"""HRA API Client."""
from collections import defaultdict
from datetime import datetime

import httpx
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client

BASE_URL = "https://api.hra.no"
DEFAULT_WEEKS = 12


class HraApiError(Exception):
    """Base exception for HRA API errors."""


class HraApiClient:
    """Client for HRA Recycling API."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        self._hass = hass
        self._address = address
        self.agreement_id: str = ""

    @property
    def address(self) -> str:
        return self._address

    async def async_resolve_address(self) -> str:
        """Resolve the configured address and return the agreement ID."""
        await self._fetch_agreement_id()
        return self.agreement_id

    async def async_get_pickup_data(self) -> dict:
        """Fetch and return pickup data."""
        if not self.agreement_id:
            await self._fetch_agreement_id()
        return await self._fetch_pickup_schedule()

    async def _fetch_agreement_id(self) -> None:
        """Fetch agreement ID from address."""
        if not self._address:
            raise HraApiError("Address is empty")

        client = get_async_client(self._hass)
        url = f"{BASE_URL}/search/address?query={self._address}"

        try:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
        except httpx.TimeoutException as err:
            raise HraApiError("Request timed out") from err
        except httpx.HTTPStatusError as err:
            raise HraApiError(f"HTTP error: {err.response.status_code}") from err

        data = response.json()
        if not data:
            raise HraApiError("Address not found")

        self._address = data[0]["name"]
        self.agreement_id = data[0]["agreementGuid"]

    async def _fetch_pickup_schedule(self) -> dict:
        """Fetch pickup schedule from JSON API."""
        client = get_async_client(self._hass)
        url = f"{BASE_URL}/Renovation/UpcomingGarbageDisposals/{self.agreement_id}?weeks={DEFAULT_WEEKS}"

        try:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
        except httpx.TimeoutException as err:
            raise HraApiError("Request timed out") from err
        except httpx.HTTPStatusError as err:
            raise HraApiError(f"HTTP error: {err.response.status_code}") from err

        return self._parse_json_response(response.json())

    def _parse_json_response(self, data: list) -> dict:
        """Parse JSON response into structured data."""
        waste_data: dict[str, list[datetime]] = defaultdict(list)

        for item in data:
            name = item["name"]
            date_str = item["date"]
            # Parse ISO format date (e.g., "2026-01-20T00:00:00")
            pickup_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            waste_data[name].append(pickup_date)

        # Sort dates within each waste type
        for dates in waste_data.values():
            dates.sort()

        return dict(sorted(waste_data.items()))
