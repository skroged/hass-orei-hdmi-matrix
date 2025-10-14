"""Select entities for OREI HDMI Matrix."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_INPUTS,
    CONF_OUTPUTS,
    CONF_NAME,
    CONF_ENABLED,
    CONF_AVAILABLE_INPUTS,
    CONF_INPUT_ENABLED,
    DOMAIN,
    NUM_INPUTS,
    NUM_OUTPUTS,
)
from .coordinator import OreiHdmiMatrixCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OREI HDMI Matrix select entities."""
    coordinator: OreiHdmiMatrixCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    outputs = entry.data.get(CONF_OUTPUTS, {})
    
    # Create a select entity for each enabled output
    for output_num in range(1, NUM_OUTPUTS + 1):
        output_config = outputs.get(str(output_num), {})
        if output_config.get(CONF_ENABLED, True):
            entities.append(
                OreiHdmiMatrixOutputSelect(coordinator, entry, output_num)
            )

    async_add_entities(entities)


class OreiHdmiMatrixOutputSelect(
    CoordinatorEntity[OreiHdmiMatrixCoordinator], SelectEntity
):
    """Select entity for choosing input for an output."""

    def __init__(self, coordinator: OreiHdmiMatrixCoordinator, entry: ConfigEntry, output_num: int) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._output_num = output_num
        self._entry = entry
        
        # Get output configuration
        outputs = entry.data.get(CONF_OUTPUTS, {})
        output_config = outputs.get(str(output_num), {})
        output_name = output_config.get(CONF_NAME, f"Output {output_num}")
        
        self._attr_unique_id = f"{entry.entry_id}_output_{output_num}"
        self._attr_name = f"{output_name} Input"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{entry.entry_id}_output_{output_num}")},
            "name": output_name,
            "manufacturer": "OREI",
            "model": "8x8 HDMI Matrix",
            "via_device": (DOMAIN, entry.entry_id),
        }

    @property
    def options(self) -> list[str]:
        """Return the available options."""
        # Get configured inputs
        inputs = self._entry.data.get(CONF_INPUTS, {})
        outputs = self._entry.data.get(CONF_OUTPUTS, {})
        output_config = outputs.get(str(self._output_num), {})
        available_inputs = output_config.get(CONF_AVAILABLE_INPUTS, list(range(1, NUM_INPUTS + 1)))
        
        # Build list of available input names (only enabled inputs)
        options = []
        for input_num in available_inputs:
            input_config = inputs.get(str(input_num), {})
            # Only include enabled inputs
            if input_config.get(CONF_INPUT_ENABLED, True):
                input_name = input_config.get(CONF_NAME, f"Input {input_num}")
                options.append(input_name)
        
        return options

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        source_mapping = self.coordinator.data.get("source_mapping", [])
        if len(source_mapping) >= self._output_num:
            current_input = source_mapping[self._output_num - 1]
            if 1 <= current_input <= NUM_INPUTS:
                # Get configured input name
                inputs = self._entry.data.get(CONF_INPUTS, {})
                input_config = inputs.get(str(current_input), {})
                input_name = input_config.get(CONF_NAME, f"Input {current_input}")
                return input_name
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the input number for the selected option by matching configured names
        inputs = self._entry.data.get(CONF_INPUTS, {})
        input_num = None
        
        for i in range(1, NUM_INPUTS + 1):
            input_config = inputs.get(str(i), {})
            input_name = input_config.get(CONF_NAME, f"Input {i}")
            if input_name == option:
                input_num = i
                break
        
        if input_num is None:
            _LOGGER.error("Could not find input number for option: %s", option)
            return

        if not (1 <= input_num <= NUM_INPUTS):
            _LOGGER.error("Invalid input number: %d", input_num)
            return

        success = await self.coordinator.async_set_output_input(self._output_num, input_num)
        if not success:
            _LOGGER.error("Failed to set output %d to input %d", self._output_num, input_num)
            # The coordinator will handle updating the data on success
