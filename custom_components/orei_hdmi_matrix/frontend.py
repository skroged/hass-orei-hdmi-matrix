"""Frontend setup for OREI HDMI Matrix integration."""

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.core import HomeAssistant


async def async_setup_frontend(hass: HomeAssistant) -> None:
    """Set up the frontend components."""
    # Add the custom more-info dialog JavaScript
    add_extra_js_url(hass, "/local/more-info-orei_hdmi_matrix.js")
