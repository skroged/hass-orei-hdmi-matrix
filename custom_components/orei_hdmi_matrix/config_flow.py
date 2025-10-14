"""Config flow for OREI HDMI Matrix integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import OreiHdmiMatrixApi, OreiHdmiMatrixApiError
from .const import (
    CONF_INPUTS,
    CONF_OUTPUTS,
    CONF_NAME,
    CONF_ENABLED,
    CONF_AVAILABLE_INPUTS,
    DEFAULT_PASSWORD,
    DEFAULT_USERNAME,
    DOMAIN,
    NUM_INPUTS,
    NUM_OUTPUTS,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
    }
)


def create_default_config() -> dict[str, Any]:
    """Create default configuration for inputs and outputs."""
    inputs = {}
    outputs = {}
    
    # Create default input configuration
    for i in range(1, NUM_INPUTS + 1):
        inputs[str(i)] = {
            CONF_NAME: f"Input {i}",
        }
    
    # Create default output configuration
    for i in range(1, NUM_OUTPUTS + 1):
        outputs[str(i)] = {
            CONF_NAME: f"Output {i}",
            CONF_ENABLED: True,
            CONF_AVAILABLE_INPUTS: list(range(1, NUM_INPUTS + 1)),  # All inputs available by default
        }
    
    return {CONF_INPUTS: inputs, CONF_OUTPUTS: outputs}


def clean_host(host: str) -> str:
    """Clean the host input by removing protocol if present."""
    host = host.strip()
    if host.startswith(('http://', 'https://')):
        host = host.split('://', 1)[1]
    # Remove trailing slash if present
    if host.endswith('/'):
        host = host[:-1]
    return host


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Clean the host input
    clean_host_value = clean_host(data[CONF_HOST])
    
    async with OreiHdmiMatrixApi(
        host=clean_host_value,
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
    ) as api:
        if not await api.authenticate():
            raise CannotConnect

        # Get device info to confirm connection
        status = await api.get_status()
        return {"title": f"OREI HDMI Matrix ({clean_host_value})", "status": status}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OREI HDMI Matrix."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            # Add default configuration for inputs and outputs
            config_data = user_input.copy()
            # Clean the host value before saving
            config_data[CONF_HOST] = clean_host(user_input[CONF_HOST])
            config_data.update(create_default_config())
            return self.async_create_entry(title=info["title"], data=config_data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    async def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for OREI HDMI Matrix."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update the configuration
            new_data = self.config_entry.data.copy()
            new_data.update(user_input)
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data={})

        # Create schema for inputs
        input_fields = {}
        inputs = self.config_entry.data.get(CONF_INPUTS, {})
        for i in range(1, NUM_INPUTS + 1):
            input_key = f"input_{i}_name"
            default_name = inputs.get(str(i), {}).get(CONF_NAME, f"Input {i}")
            input_fields[vol.Required(input_key, default=default_name)] = str

        # Create schema for outputs
        output_fields = {}
        outputs = self.config_entry.data.get(CONF_OUTPUTS, {})
        for i in range(1, NUM_OUTPUTS + 1):
            # Output name
            name_key = f"output_{i}_name"
            default_name = outputs.get(str(i), {}).get(CONF_NAME, f"Output {i}")
            output_fields[vol.Required(name_key, default=default_name)] = str
            
            # Output enabled
            enabled_key = f"output_{i}_enabled"
            default_enabled = outputs.get(str(i), {}).get(CONF_ENABLED, True)
            output_fields[vol.Required(enabled_key, default=default_enabled)] = bool

        schema = vol.Schema({**input_fields, **output_fields})
        
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
