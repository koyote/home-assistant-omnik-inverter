"""Config flow for Omnik Inverter integration."""
from __future__ import annotations

import socket
from typing import Any

from omnikinverter import OmnikInverter, OmnikInverterError
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TYPE,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SOURCE_TYPE,
    CONF_SERIAL,
    CONFIGFLOW_VERSION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


async def validate_input(user_input: dict[str, Any]) -> str | None:
    """Validate the user input."""
    host = user_input[CONF_HOST]
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        raise Exception("invalid_host")


class OmnikInverterFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config flow for Omnik Inverter."""

    VERSION = CONFIGFLOW_VERSION

    def __init__(self):
        """Initialize with empty source type."""
        self.source_type = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OmnikInverterOptionsFlowHandler:
        """Get the options flow for this handler."""
        return OmnikInverterOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input=None, errors: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        errors = {}
        if user_input is not None:
            user_selection = user_input[CONF_TYPE]
            self.source_type = user_selection.lower()
            if user_selection == "HTML" or user_selection == "CGI":
                return await self.async_step_setup_html_or_cgi()
            elif user_selection == "TCP":
                return await self.async_step_setup_tcp()
            return await self.async_step_setup()

        list_of_types = ["Javascript", "JSON", "HTML", "TCP", "CGI"]

        schema = vol.Schema({vol.Required(CONF_TYPE): vol.In(list_of_types)})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_setup(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle setup flow for the JS and JSON route."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                async with OmnikInverter(
                    host=user_input[CONF_HOST],
                    source_type=self.source_type,
                ) as client:
                    await client.inverter()
            except OmnikInverterError:
                errors["base"] = "cannot_connect"
            except Exception as error:  # pylint: disable=broad-except
                errors["base"] = str(error)
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_SOURCE_TYPE: self.source_type,
                    },
                )

        return self.async_show_form(
            step_id="setup",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(CONF_HOST): str,
                }
            ),
            errors=errors,
        )

    async def async_step_setup_html_or_cgi(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle setup flow for html and cgi route."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                async with OmnikInverter(
                    host=user_input[CONF_HOST],
                    source_type=self.source_type,
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                ) as client:
                    await client.inverter()
            except OmnikInverterError:
                errors["base"] = "cannot_connect"
            except Exception as error:  # pylint: disable=broad-except
                errors["base"] = str(error)
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_SOURCE_TYPE: self.source_type,
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="setup_html_or_cgi",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_setup_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle setup flow for TCP route."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                async with OmnikInverter(
                    host=user_input[CONF_HOST],
                    source_type=self.source_type,
                    serial_number=user_input[CONF_SERIAL],
                ) as client:
                    await client.inverter()
            except OmnikInverterError:
                errors["base"] = "cannot_connect"
            except Exception as error:  # pylint: disable=broad-except
                errors["base"] = str(error)
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_SOURCE_TYPE: self.source_type,
                        CONF_SERIAL: user_input[CONF_SERIAL],
                    },
                )

        return self.async_show_form(
            step_id="setup_tcp",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NAME, default=self.hass.config.location_name
                    ): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_SERIAL): int,
                }
            ),
            errors=errors,
        )


class OmnikInverterOptionsFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Mange the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1)),
                }
            ),
        )
