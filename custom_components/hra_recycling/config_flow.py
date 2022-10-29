"""Adds config flow for Blueprint."""
from statistics import mode
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import selector
import voluptuous as vol

from .api import ApiClient
from .const import (
    CONF_ADDRESS,
    DOMAIN,
    PLATFORMS,
)


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

            valid = True
            if valid:
                return self.async_create_entry(
                    # title=user_input[CONF_ADDRESS], data=user_input
                    title="Hadeland Ringerike Avfallsselskap",
                    data=user_input,
                )
            else:  # The address is not correct
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_ADDRESS] = "Musmyrvegen 10, 3520 Jevnaker"

        return await self._show_config_form(user_input)

    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry):
    #     return BlueprintOptionsFlowHandler(config_entry)
    # get_options_flow() viser en konfigurasjons-skjerm for å endre på innstil

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        scheme = vol.Schema(
            {vol.Required(CONF_ADDRESS, default=user_input[CONF_ADDRESS]): str}
        )

        return self.async_show_form(
            step_id="user", data_schema=scheme, errors=self._errors
        )


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
#                     # https://developers.home-assistant.io/docs/development_validation/ for all the types.
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
