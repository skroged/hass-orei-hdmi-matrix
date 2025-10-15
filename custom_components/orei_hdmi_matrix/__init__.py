"""OREI HDMI Matrix integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import OreiHdmiMatrixCoordinator
from .frontend import async_setup_frontend

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OREI HDMI Matrix from a config entry."""
    coordinator = OreiHdmiMatrixCoordinator(hass, entry)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        raise ConfigEntryNotReady(f"Error connecting to OREI HDMI Matrix: {ex}") from ex

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def async_refresh_service(service_call):
        """Handle refresh service call."""
        device_id = service_call.data.get("device_id")
        if device_id:
            # Find the coordinator for this device
            for entry_id, coord in hass.data[DOMAIN].items():
                if coord.entry.entry_id == entry_id:
                    await coord.async_refresh_now()
                    break
        else:
            # Refresh all coordinators
            for coord in hass.data[DOMAIN].values():
                await coord.async_refresh_now()

    hass.services.async_register(DOMAIN, "refresh", async_refresh_service)

    # Set up custom more-info dialog
    await async_setup_frontend(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
