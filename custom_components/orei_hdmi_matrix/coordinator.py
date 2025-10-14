"""Data coordinator for OREI HDMI Matrix."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OreiHdmiMatrixApi, OreiHdmiMatrixApiError
from .const import DEFAULT_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class OreiHdmiMatrixCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data coordinator for OREI HDMI Matrix."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        # Get update interval from config or use default
        update_interval_seconds = entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)
        update_interval = timedelta(seconds=update_interval_seconds)
        
        super().__init__(
            hass,
            _LOGGER,
            name="OREI HDMI Matrix",
            update_interval=update_interval,
        )
        self.entry = entry
        self.api: OreiHdmiMatrixApi | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via API."""
        if not self.api:
            self.api = OreiHdmiMatrixApi(
                host=self.entry.data["host"],
                username=self.entry.data["username"],
                password=self.entry.data["password"],
            )
            await self.api.__aenter__()

        try:
            _LOGGER.debug("Polling OREI HDMI Matrix for status updates")
            status = await self.api.get_status()
            _LOGGER.debug("Successfully polled matrix status: %s", status)
            return status
        except OreiHdmiMatrixApiError as err:
            _LOGGER.error("Failed to poll OREI HDMI Matrix: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_set_output_input(self, output: int, input_: int) -> bool:
        """Set which input is connected to an output."""
        if not self.api:
            return False
            
        try:
            success = await self.api.set_output_input(output, input_)
            if success:
                # Update our data immediately after a successful change
                _LOGGER.debug("Output %d set to input %d, refreshing data", output, input_)
                await self.async_request_refresh()
            return success
        except OreiHdmiMatrixApiError as err:
            _LOGGER.error("Error setting output %d to input %d: %s", output, input_, err)
            return False

    async def async_refresh_now(self) -> None:
        """Force an immediate refresh of the data."""
        _LOGGER.debug("Forcing immediate refresh of OREI HDMI Matrix data")
        await self.async_request_refresh()

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator and close API session."""
        if self.api:
            await self.api.__aexit__(None, None, None)
            self.api = None
