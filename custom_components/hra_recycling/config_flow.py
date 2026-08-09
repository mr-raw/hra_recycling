"""Config flow for HRA Recycling."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_ADDRESS, CONF_ENABLE_CALENDAR, DOMAIN, LOGGER
from .hra_api import HraApiClient, HraApiError


class HraConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for HRA Recycling."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._address: str = ""

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HraOptionsFlow:
        """Return the options flow handler."""
        return HraOptionsFlow()

    async def async_step_user(self, user_input: dict | None = None):
        """Handle address input step."""
        errors = {}

        if user_input:
            client = HraApiClient(self.hass, user_input[CONF_ADDRESS])
            try:
                agreement_id = await client.async_resolve_address()
            except HraApiError as err:
                LOGGER.warning("Address validation failed: %s", err)
                errors["base"] = "invalid_address"
            else:
                # One entry per agreement, so the same address cannot be added
                # twice and collide on entity unique IDs.
                await self.async_set_unique_id(agreement_id)
                self._abort_if_unique_id_configured()
                self._address = client.address
                return await self.async_step_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ADDRESS): selector.TextSelector(),
            }),
            errors=errors,
        )

    async def async_step_options(self, user_input: dict | None = None):
        """Handle options step."""
        if user_input is not None:
            return self.async_create_entry(
                title=self._address,
                data={CONF_ADDRESS: self._address},
                options={
                    CONF_ENABLE_CALENDAR: user_input.get(CONF_ENABLE_CALENDAR, True)
                },
            )

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Required(CONF_ENABLE_CALENDAR, default=True): selector.BooleanSelector(),
            }),
        )


class HraOptionsFlow(config_entries.OptionsFlow):
    """Handle options after setup."""

    async def async_step_init(self, user_input: dict | None = None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_ENABLE_CALENDAR,
            self.config_entry.data.get(CONF_ENABLE_CALENDAR, True),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_ENABLE_CALENDAR, default=current): selector.BooleanSelector(),
            }),
        )
