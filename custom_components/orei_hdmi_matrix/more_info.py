"""More info dialog handler for OREI HDMI Matrix entities."""

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the more info dialog."""
    # Add the custom card JavaScript
    add_extra_js_url(hass, f"/local/orei-hdmi-matrix-card.js")
    
    return True


def get_more_info_config(entity_id: str, entity_state: dict) -> dict:
    """Get configuration for the custom more info dialog."""
    return {
        "type": "custom:orei-hdmi-matrix-card",
        "entity": entity_id,
        "name": entity_state.get("attributes", {}).get("friendly_name", "HDMI Matrix"),
        "device_name": entity_state.get("attributes", {}).get("device_name", "HDMI Matrix"),
        "value": entity_state.get("state"),
        "options": entity_state.get("attributes", {}).get("options", []),
    }
