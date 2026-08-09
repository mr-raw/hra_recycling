"""Config flow for HRA Recycling."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector
from homeassistant.helpers.translation import async_get_translations

from .const import (
    CONF_ADDRESS,
    CONF_ENABLE_CALENDAR,
    CONF_TRACKED_FRACTIONS,
    CONF_WEEKS,
    DEFAULT_WEEKS,
    DOMAIN,
    LOGGER,
    MAX_WEEKS,
    MIN_WEEKS,
    WASTE_TYPES,
)
from .hra_api import HraApiClient, HraApiError
from .options import calendar_enabled, configured_weeks, tracked_fractions


async def _fraction_options(
    hass: HomeAssistant, available: list[str]
) -> list[selector.SelectOptionDict]:
    """Label the fractions with the same names their sensors carry.

    The API returns Norwegian labels, so without this the checkboxes would stay
    Norwegian in every other language while the sensors were translated.
    """
    translations = await async_get_translations(
        hass, hass.config.language, "entity", {DOMAIN}
    )

    options = [
        selector.SelectOptionDict(
            value=fraction,
            label=translations.get(
                f"component.{DOMAIN}.entity.sensor.{WASTE_TYPES[fraction]}.name",
                fraction,
            )
            if fraction in WASTE_TYPES
            else fraction,
        )
        for fraction in available
    ]
    return sorted(options, key=lambda option: option["label"])


def _weeks_selector() -> selector.NumberSelector:
    """Return the selector for the fetch window."""
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=MIN_WEEKS,
            max=MAX_WEEKS,
            step=1,
            mode=selector.NumberSelectorMode.BOX,
        )
    )


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
        """Handle options step.

        Fractions are not offered here: which ones exist is only known once a
        schedule has been fetched, so that choice lives in the options flow.
        """
        if user_input is not None:
            return self.async_create_entry(
                title=self._address,
                data={CONF_ADDRESS: self._address},
                options={
                    CONF_ENABLE_CALENDAR: user_input[CONF_ENABLE_CALENDAR],
                    CONF_WEEKS: int(user_input[CONF_WEEKS]),
                },
            )

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema({
                vol.Required(CONF_ENABLE_CALENDAR, default=True): selector.BooleanSelector(),
                vol.Required(CONF_WEEKS, default=DEFAULT_WEEKS): _weeks_selector(),
            }),
        )


class HraOptionsFlow(config_entries.OptionsFlow):
    """Handle options after setup."""

    async def async_step_init(self, user_input: dict | None = None):
        """Manage the options."""
        entry = self.config_entry
        coordinator = getattr(entry, "runtime_data", None)

        # Offer whatever the address actually has a schedule for.
        available = sorted(
            set(WASTE_TYPES) | set(getattr(coordinator, "data", None) or {})
        )
        errors = {}

        if user_input is not None:
            if not user_input.get(CONF_TRACKED_FRACTIONS):
                errors["base"] = "no_fractions"
            else:
                return self.async_create_entry(
                    data={
                        CONF_TRACKED_FRACTIONS: user_input[CONF_TRACKED_FRACTIONS],
                        CONF_ENABLE_CALENDAR: user_input[CONF_ENABLE_CALENDAR],
                        CONF_WEEKS: int(user_input[CONF_WEEKS]),
                    }
                )
            current = user_input
        else:
            current = {
                CONF_TRACKED_FRACTIONS: sorted(tracked_fractions(entry, available)),
                CONF_ENABLE_CALENDAR: calendar_enabled(entry),
                CONF_WEEKS: configured_weeks(entry),
            }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_TRACKED_FRACTIONS,
                    default=current.get(CONF_TRACKED_FRACTIONS, available),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=await _fraction_options(self.hass, available),
                        multiple=True,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                ),
                vol.Required(
                    CONF_ENABLE_CALENDAR,
                    default=current.get(CONF_ENABLE_CALENDAR, True),
                ): selector.BooleanSelector(),
                vol.Required(
                    CONF_WEEKS, default=current.get(CONF_WEEKS, DEFAULT_WEEKS)
                ): _weeks_selector(),
            }),
            errors=errors,
        )
