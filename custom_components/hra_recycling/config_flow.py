"""config_flow.py"""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_ADDRESS, DOMAIN, LOGGER
from .hra_api import (
    ApiClientNoPickupDataFound,
    ApiClientCommunicationError,
    ApiClientError,
    HraApiClient,
)


class HRAConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HRA Recycling."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._check_if_address_is_correct(
                    address=user_input[CONF_ADDRESS]
                )
            except ApiClientNoPickupDataFound as exception:
                LOGGER.warning(exception)
                _errors["base"] = "invalid_address"
            except ApiClientCommunicationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "comm_error"
            except ApiClientError as exception:
                LOGGER.error(exception)
                _errors["base"] = "unknown_error"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_ADDRESS], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ADDRESS,
                        default=(user_input or {}).get(CONF_ADDRESS),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def _check_if_address_is_correct(self, address):
        """Checks if the provided address is correct."""
        client = HraApiClient(address=address)
        await client.async_verify_address()
