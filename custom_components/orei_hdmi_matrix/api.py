"""API client for OREI HDMI Matrix."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientTimeout

from .const import (
    API_ENDPOINT,
    CMD_GET_STATUS,
    CMD_LOGIN,
    CMD_VIDEO_SWITCH,
    DEFAULT_TIMEOUT,
    NUM_INPUTS,
    NUM_OUTPUTS,
)

_LOGGER = logging.getLogger(__name__)


class OreiHdmiMatrixApiError(Exception):
    """Exception raised for API errors."""


class OreiHdmiMatrixApi:
    """API client for OREI HDMI Matrix."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the API client."""
        self.host = host
        self.username = username
        self.password = password
        self.timeout = ClientTimeout(total=timeout)
        self._session: aiohttp.ClientSession | None = None
        self._authenticated = False

    async def __aenter__(self) -> OreiHdmiMatrixApi:
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._session:
            await self._session.close()

    async def _request(self, data: dict[str, Any]) -> dict[str, Any]:
        """Make a request to the API."""
        if not self._session:
            raise OreiHdmiMatrixApiError("Session not initialized")

        url = f"http://{self.host}{API_ENDPOINT}"
        _LOGGER.debug("Making API request to %s with data: %s", url, data)
        
        try:
            async with self._session.post(url, json=data) as response:
                _LOGGER.debug("API response status: %s", response.status)
                _LOGGER.debug("API response content-type: %s", response.headers.get('content-type', 'unknown'))
                
                if response.status != 200:
                    response_text = await response.text()
                    _LOGGER.error("HTTP error %s: %s, response: %s", response.status, response.reason, response_text)
                    raise OreiHdmiMatrixApiError(
                        f"HTTP error {response.status}: {response.reason}"
                    )
                
                # Get the response text first to see what we're dealing with
                response_text = await response.text()
                _LOGGER.debug("API response text: %s", response_text)
                
                # Try to parse as JSON
                try:
                    import json
                    result = json.loads(response_text)
                    _LOGGER.debug("API response JSON: %s", result)
                    return result
                except json.JSONDecodeError as json_err:
                    _LOGGER.error("Failed to parse JSON response: %s, response text: %s", json_err, response_text)
                    # If it's not JSON, it might be plain text - let's try to handle it
                    raise OreiHdmiMatrixApiError(f"Invalid JSON response: {response_text}")
                
        except aiohttp.ClientError as err:
            _LOGGER.error("Request failed to %s: %s", url, err)
            raise OreiHdmiMatrixApiError(f"Request failed: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error during API request to %s: %s", url, err)
            raise OreiHdmiMatrixApiError(f"Unexpected error: {err}") from err

    async def authenticate(self) -> bool:
        """Authenticate with the matrix."""
        data = {
            "comhead": CMD_LOGIN,
            "user": self.username,
            "password": self.password,
        }
        
        try:
            _LOGGER.info("Authenticating with OREI HDMI Matrix at %s", self.host)
            result = await self._request(data)
            _LOGGER.debug("Authentication response: %s", result)
            
            success = result.get("result") == 1
            self._authenticated = success
            
            if success:
                _LOGGER.info("Successfully authenticated with OREI HDMI Matrix")
            else:
                _LOGGER.error("Authentication failed - result: %s", result.get("result"))
                
            return success
            
        except OreiHdmiMatrixApiError as err:
            _LOGGER.error("Authentication error: %s", err)
            self._authenticated = False
            return False

    async def get_status(self) -> dict[str, Any]:
        """Get the current status of the matrix."""
        if not self._authenticated:
            await self.authenticate()
            
        data = {
            "comhead": CMD_GET_STATUS,
            "language": 0,
        }
        
        result = await self._request(data)
        
        # Parse the allsource array to create a mapping
        all_source = result.get("allsource", [])
        if len(all_source) >= NUM_OUTPUTS:
            # Remove the trailing 0 if present
            source_mapping = all_source[:NUM_OUTPUTS]
        else:
            source_mapping = all_source
            
        return {
            "power": result.get("power", 0),
            "source_mapping": source_mapping,
            "input_names": result.get("allinputname", []),
            "output_names": result.get("alloutputname", []),
            "preset_names": result.get("allname", []),
        }

    async def set_output_input(self, output: int, input_: int) -> bool:
        """Set which input is connected to an output."""
        if not self._authenticated:
            await self.authenticate()
            
        if not (1 <= output <= NUM_OUTPUTS):
            raise ValueError(f"Output must be between 1 and {NUM_OUTPUTS}")
        if not (1 <= input_ <= NUM_INPUTS):
            raise ValueError(f"Input must be between 1 and {NUM_INPUTS}")
            
        data = {
            "comhead": CMD_VIDEO_SWITCH,
            "language": 0,
            "source": [output, input_],
        }
        
        result = await self._request(data)
        success = result.get("result") == 1
        
        if success:
            _LOGGER.info("Successfully set output %d to input %d", output, input_)
        else:
            _LOGGER.error("Failed to set output %d to input %d", output, input_)
            
        return success
