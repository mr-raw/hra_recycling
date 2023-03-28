"""config_flow.py"""
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol
from .hra_api import ApiClient
from .const import CONF_ADDRESS, DOMAIN


class HRAConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HRA Recycling."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self.api_client = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            # Check if the address is correct here
            valid = await self._check_if_address_is_correct(user_input[CONF_ADDRESS])
            if valid:
                return self.async_create_entry(
                    title=self.api_client.address,
                    data={
                        "address": self.api_client.address,
                        "agreement_id": self.api_client.agreement_id,
                    },
                )
            else:  # The address is not correct
                self._errors["base"] = "invalid_address"

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_ADDRESS] = "Rådhusvegen 39"

        return await self._show_config_form(user_input)

    async def _check_if_address_is_correct(self, address):
        """Return true if address is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = ApiClient(address, session)
            temp = await client.async_verify_address()
            # Original code:
            # if len(temp) == 1:
            #     client.agreement_id = temp[0].get("agreementGuid")
            #     self.api_client = client
            #     return True
            # TODO: This does not check how many results, only return the first.
            # We should probably do some more with this. Maybe show the results and make
            # the user choose the correct one.
            client.agreement_id = temp[0].get("agreementGuid")
            self.api_client = client
            return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        scheme = vol.Schema(
            {vol.Required(CONF_ADDRESS, default=user_input[CONF_ADDRESS]): str}
        )

        return self.async_show_form(
            step_id="user", data_schema=scheme, errors=self._errors
        )
