"""Select entities for OREI HDMI Matrix."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NUM_INPUTS, NUM_OUTPUTS
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
    
    # Create a select entity for each output
    for output_num in range(1, NUM_OUTPUTS + 1):
        entities.append(
            OreiHdmiMatrixOutputSelect(coordinator, output_num)
        )

    async_add_entities(entities)


class OreiHdmiMatrixOutputSelect(
    CoordinatorEntity[OreiHdmiMatrixCoordinator], SelectEntity
):
    """Select entity for choosing input for an output."""

    def __init__(self, coordinator: OreiHdmiMatrixCoordinator, output_num: int) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._output_num = output_num
        self._attr_unique_id = f"{coordinator.entry.entry_id}_output_{output_num}"
        self._attr_name = f"Output {output_num} Input"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "OREI HDMI Matrix",
            "manufacturer": "OREI",
            "model": "8x8 HDMI Matrix",
        }

    @property
    def options(self) -> list[str]:
        """Return the available options."""
        input_names = self.coordinator.data.get("input_names", [])
        if not input_names:
            # Fallback to generic names if we don't have the actual names
            return [f"Input {i}" for i in range(1, NUM_INPUTS + 1)]
        return input_names

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        source_mapping = self.coordinator.data.get("source_mapping", [])
        if len(source_mapping) >= self._output_num:
            current_input = source_mapping[self._output_num - 1]
            if 1 <= current_input <= NUM_INPUTS:
                input_names = self.coordinator.data.get("input_names", [])
                if input_names and len(input_names) >= current_input:
                    return input_names[current_input - 1]
                else:
                    return f"Input {current_input}"
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Find the input number for the selected option
        input_names = self.coordinator.data.get("input_names", [])
        if input_names and option in input_names:
            input_num = input_names.index(option) + 1
        else:
            # Fallback: try to extract number from "Input X" format
            try:
                input_num = int(option.split()[-1])
            except (ValueError, IndexError):
                _LOGGER.error("Could not determine input number for option: %s", option)
                return

        if not (1 <= input_num <= NUM_INPUTS):
            _LOGGER.error("Invalid input number: %d", input_num)
            return

        success = await self.coordinator.async_set_output_input(self._output_num, input_num)
        if not success:
            _LOGGER.error("Failed to set output %d to input %d", self._output_num, input_num)
            # The coordinator will handle updating the data on success
