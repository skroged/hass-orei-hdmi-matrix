"""Tests for the OREI HDMI Matrix config flow."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.components.orei_hdmi_matrix.config_flow import CannotConnect, InvalidAuth
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.orei_hdmi_matrix.const import DOMAIN


@pytest.fixture
def mock_api():
    """Mock the API client."""
    with patch("custom_components.orei_hdmi_matrix.config_flow.OreiHdmiMatrixApi") as mock:
        api_instance = AsyncMock()
        mock.return_value.__aenter__.return_value = api_instance
        yield api_instance


async def test_form(hass: HomeAssistant, mock_api) -> None:
    """Test we get the form."""
    mock_api.authenticate.return_value = True
    mock_api.get_status.return_value = {
        "power": 1,
        "source_mapping": [1, 2, 3, 4, 5, 6, 7, 8],
        "input_names": ["Input1", "Input2", "Input3", "Input4", "Input5", "Input6", "Input7", "Input8"],
        "output_names": ["Output1", "Output2", "Output3", "Output4", "Output5", "Output6", "Output7", "Output8"],
        "preset_names": ["Preset1", "Preset2", "Preset3", "Preset4", "Preset5", "Preset6", "Preset7", "Preset8"]
    }

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "host": "192.168.1.100",
            "username": "Admin",
            "password": "admin",
        },
    )
    await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "OREI HDMI Matrix (192.168.1.100)"
    assert result2["data"] == {
        "host": "192.168.1.100",
        "username": "Admin",
        "password": "admin",
    }


async def test_form_cannot_connect(hass: HomeAssistant, mock_api) -> None:
    """Test we handle cannot connect error."""
    mock_api.authenticate.return_value = False

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "host": "192.168.1.100",
            "username": "Admin",
            "password": "admin",
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_invalid_auth(hass: HomeAssistant, mock_api) -> None:
    """Test we handle invalid auth error."""
    mock_api.authenticate.side_effect = InvalidAuth

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "host": "192.168.1.100",
            "username": "Admin",
            "password": "wrong_password",
        },
    )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_auth"}
