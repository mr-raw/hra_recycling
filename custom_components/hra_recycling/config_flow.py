"""The Config Flow"""
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import voluptuous as vol

from .api import ApiClient
from .const import CONF_ADDRESS, DOMAIN


class HRAConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            # Check if the address is correct here

            valid = await self._check_if_address_is_correct(user_input[CONF_ADDRESS])
            if valid:
                return self.async_create_entry(
                    title=user_input[CONF_ADDRESS],
                    data=user_input,
                )
            else:  # The address is not correct
                self._errors["base"] = "invalid_address"

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_ADDRESS] = "Rådhusvegen 39"
        # At a later stage, it will be possible to choose the area

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        scheme = vol.Schema(
            {vol.Required(CONF_ADDRESS, default=user_input[CONF_ADDRESS]): str}
        )

        return self.async_show_form(
            step_id="user", data_schema=scheme, errors=self._errors
        )

    async def _check_if_address_is_correct(self, address):
        """Return true if address is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = ApiClient(address, session)
            temp = await client.async_verify_address()
            if len(temp) == 1:
                client.agreement_id = temp[0].get("agreementGuid")
                return True
        except Exception:  # pylint: disable=broad-except
            pass
        return False


# class BlueprintOptionsFlowHandler(config_entries.OptionsFlow):
#     """Blueprint config flow options handler."""

#     def __init__(self, config_entry):
#         """Initialize HACS options flow."""
#         self.config_entry = config_entry
#         self.options = dict(config_entry.options)

#     async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
#         """Manage the options."""
#         return await self.async_step_user()

#     async def async_step_user(self, user_input=None):
#         """Handle a flow initialized by the user."""
#         if user_input is not None:
#             self.options.update(user_input)
#             return await self._update_options()

#         return self.async_show_form(
#             step_id="user",
#             data_schema=vol.Schema(
#                 {
#                     # https://developers.home-assistant.io/docs/development_validation/
# for all the types.
#                     vol.Required(x, default=self.options.get(x, True)): bool
#                     for x in sorted(PLATFORMS)
#                 }
#             ),
#         )

#     async def _update_options(self):
#         """Update config entry options."""
#         return self.async_create_entry(
#             title=self.config_entry.data.get(CONF_ADDRESS), data=self.options
#         )
