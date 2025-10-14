"""Data coordinator for OREI HDMI Matrix."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OreiHdmiMatrixApi, OreiHdmiMatrixApiError
from .const import UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class OreiHdmiMatrixCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data coordinator for OREI HDMI Matrix."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="OREI HDMI Matrix",
            update_interval=UPDATE_INTERVAL,
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
            return await self.api.get_status()
        except OreiHdmiMatrixApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_set_output_input(self, output: int, input_: int) -> bool:
        """Set which input is connected to an output."""
        if not self.api:
            return False
            
        try:
            success = await self.api.set_output_input(output, input_)
            if success:
                # Update our data immediately after a successful change
                await self.async_request_refresh()
            return success
        except OreiHdmiMatrixApiError as err:
            _LOGGER.error("Error setting output %d to input %d: %s", output, input_, err)
            return False

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator and close API session."""
        if self.api:
            await self.api.__aexit__(None, None, None)
            self.api = None
