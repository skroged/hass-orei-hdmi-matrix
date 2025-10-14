"""Tests for the OREI HDMI Matrix API client."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.orei_hdmi_matrix.api import OreiHdmiMatrixApi, OreiHdmiMatrixApiError


@pytest.fixture
def api():
    """Create an API client instance."""
    return OreiHdmiMatrixApi("192.168.1.100", "Admin", "admin")


@pytest.mark.asyncio
async def test_authenticate_success(api):
    """Test successful authentication."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"comhead": "login", "result": 1})
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response
        
        async with api:
            result = await api.authenticate()
            
        assert result is True
        assert api._authenticated is True


@pytest.mark.asyncio
async def test_authenticate_failure(api):
    """Test failed authentication."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"comhead": "login", "result": 0})
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response
        
        async with api:
            result = await api.authenticate()
            
        assert result is False
        assert api._authenticated is False


@pytest.mark.asyncio
async def test_get_status(api):
    """Test getting device status."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "comhead": "get video status",
        "power": 1,
        "allsource": [7, 6, 2, 4, 2, 2, 2, 2, 0],
        "allinputname": ["Input1", "Input2", "Input3", "Input4", "Input5", "Input6", "Input7", "Input8"],
        "alloutputname": ["Output1", "Output2", "Output3", "Output4", "Output5", "Output6", "Output7", "Output8"],
        "allname": ["Preset1", "Preset2", "Preset3", "Preset4", "Preset5", "Preset6", "Preset7", "Preset8"]
    })
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response
        
        async with api:
            api._authenticated = True  # Skip authentication
            result = await api.get_status()
            
        assert result["power"] == 1
        assert result["source_mapping"] == [7, 6, 2, 4, 2, 2, 2, 2]
        assert len(result["input_names"]) == 8
        assert len(result["output_names"]) == 8


@pytest.mark.asyncio
async def test_set_output_input(api):
    """Test setting output to input."""
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"comhead": "video switch", "result": 1})
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response
        
        async with api:
            api._authenticated = True  # Skip authentication
            result = await api.set_output_input(1, 3)
            
        assert result is True


@pytest.mark.asyncio
async def test_set_output_input_invalid_output(api):
    """Test setting invalid output number."""
    async with api:
        with pytest.raises(ValueError, match="Output must be between 1 and 8"):
            await api.set_output_input(0, 1)
            
        with pytest.raises(ValueError, match="Output must be between 1 and 8"):
            await api.set_output_input(9, 1)


@pytest.mark.asyncio
async def test_set_output_input_invalid_input(api):
    """Test setting invalid input number."""
    async with api:
        with pytest.raises(ValueError, match="Input must be between 1 and 8"):
            await api.set_output_input(1, 0)
            
        with pytest.raises(ValueError, match="Input must be between 1 and 8"):
            await api.set_output_input(1, 9)
