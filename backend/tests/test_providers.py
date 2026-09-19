import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timezone
import httpx

from providers.base import ProviderStatus, CanonicalWeatherObservation, ProviderFetchResult
from providers.openmeteo import OpenMeteoProvider
from providers.accuweather import AccuWeatherProvider
from providers.imd import IMDProvider
from providers.registry import ProviderRegistry

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        yield mock_client

@pytest.mark.asyncio
async def test_openmeteo_successful_normalization(mock_httpx_client):
    provider = OpenMeteoProvider()
    
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "current": {
            "time": "2026-09-19T02:00:00Z",
            "rain": 12.5,
            "temperature_2m": 25.0,
            "relative_humidity_2m": 80,
            "wind_speed_10m": 15.0,
            "surface_pressure": 1010.5
        }
    }
    mock_response.raise_for_status = MagicMock()
    mock_httpx_client.get.return_value = mock_response

    result = await provider.fetch_current(17.385, 78.486)
    
    assert result.success is True
    assert result.provider_name == "OpenMeteo"
    obs = result.observation
    assert obs is not None
    assert obs.rainfall_1h_mm == 12.5
    assert obs.temperature_c == 25.0
    assert obs.humidity_percent == 80
    assert obs.wind_speed_kmh == 15.0
    assert obs.pressure_hpa == 1010.5
    assert obs.source_status == ProviderStatus.ONLINE
    assert obs.observed_at.tzinfo == timezone.utc

@pytest.mark.asyncio
async def test_openmeteo_timeout(mock_httpx_client):
    provider = OpenMeteoProvider()
    
    # Simulate timeout on all 3 attempts
    mock_httpx_client.get.side_effect = httpx.TimeoutException("Timeout")
    
    # Patch sleep to not actually sleep during test
    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await provider.fetch_current(17.385, 78.486)
        
    assert result.success is False
    assert result.error_type == ProviderStatus.TIMEOUT
    assert result.observation is None

@pytest.mark.asyncio
async def test_openmeteo_http_failure(mock_httpx_client):
    provider = OpenMeteoProvider()
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_httpx_client.get.side_effect = httpx.HTTPStatusError("500 Server Error", request=MagicMock(), response=mock_response)
    
    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await provider.fetch_current(17.385, 78.486)
        
    assert result.success is False
    assert result.error_type == ProviderStatus.SERVER_ERROR

@pytest.mark.asyncio
async def test_openmeteo_malformed_response(mock_httpx_client):
    provider = OpenMeteoProvider()
    
    mock_response = MagicMock()
    # Missing 'current' key, raises AttributeError or KeyError when parsed
    mock_response.json.return_value = {"invalid": "data"}
    mock_response.raise_for_status = MagicMock()
    mock_httpx_client.get.return_value = mock_response

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await provider.fetch_current(17.385, 78.486)
        
    assert result.success is False
    assert result.error_type == ProviderStatus.UNKNOWN

@pytest.mark.asyncio
async def test_accuweather_missing_credentials():
    # Empty API key
    provider = AccuWeatherProvider(api_key="")
    
    result = await provider.fetch_current(17.385, 78.486)
    
    assert result.success is False
    assert result.error_type == ProviderStatus.UNAVAILABLE
    assert result.error == "API key not configured"
    
    health = await provider.health_check()
    assert health == ProviderStatus.UNAVAILABLE

@pytest.mark.asyncio
async def test_accuweather_provider_unavailable(mock_httpx_client):
    provider = AccuWeatherProvider(api_key="valid")
    
    # Fail to get location key
    mock_response = MagicMock()
    mock_response.json.return_value = {} # Missing 'Key'
    mock_response.raise_for_status = MagicMock()
    mock_httpx_client.get.return_value = mock_response

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await provider.fetch_current(17.385, 78.486)
        
    assert result.success is False
    assert result.error_type == ProviderStatus.BAD_RESPONSE
    
@pytest.mark.asyncio
async def test_imd_unavailable_by_default():
    provider = IMDProvider(api_key="")
    
    result = await provider.fetch_current(17.385, 78.486)
    
    assert result.success is False
    assert result.error_type == ProviderStatus.UNAVAILABLE
    
    health = await provider.health_check()
    assert health == ProviderStatus.UNAVAILABLE

@pytest.mark.asyncio
async def test_registry_health_status(mock_httpx_client):
    registry = ProviderRegistry()
    
    p1 = OpenMeteoProvider()
    p2 = AccuWeatherProvider(api_key="")
    p3 = IMDProvider(api_key="")
    
    registry.register(p1)
    registry.register(p2)
    registry.register(p3)
    
    # Mock OpenMeteo fetch_current to return success
    with patch.object(p1, 'fetch_current', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = ProviderFetchResult(
            success=True, observation=None, error=None, error_type=None, latency_ms=10, provider_name="OpenMeteo"
        )
        
        status1 = await p1.health_check()
        assert status1 == ProviderStatus.ONLINE

    status2 = await p2.health_check()
    assert status2 == ProviderStatus.UNAVAILABLE
    
    status3 = await p3.health_check()
    assert status3 == ProviderStatus.UNAVAILABLE

@pytest.mark.asyncio
async def test_concurrent_polling_one_failing():
    registry = ProviderRegistry()
    
    p1 = OpenMeteoProvider()
    p2 = AccuWeatherProvider(api_key="mock")
    
    registry.register(p1)
    registry.register(p2)
    
    # p1 succeeds
    obs1 = CanonicalWeatherObservation(
        source_id="openmeteo", source_name="OpenMeteo", latitude=0, longitude=0, 
        observed_at=datetime.now(timezone.utc), received_at=datetime.now(timezone.utc), 
        rainfall_1h_mm=10.0, source_status=ProviderStatus.ONLINE,
        temperature_c=None, humidity_percent=None, wind_speed_kmh=None, pressure_hpa=None
    )
    res1 = ProviderFetchResult(success=True, observation=obs1, error=None, error_type=None, latency_ms=10, provider_name="OpenMeteo")
    
    # p2 throws unexpected exception (to test gather error handling)
    async def p2_fetch(*args, **kwargs):
        raise ValueError("Unexpected crash")
        
    with patch.object(p1, 'fetch_current', new_callable=AsyncMock) as mock_p1, \
         patch.object(p2, 'fetch_current', new=p2_fetch):
        
        mock_p1.return_value = res1
        
        results = await registry.fetch_all(0.0, 0.0)
        
        # We should get exactly 2 results back, gather shouldn't blow up
        assert len(results) == 2
        
        # First is OpenMeteo, should be successful
        assert results[0].success is True
        assert results[0].observation.rainfall_1h_mm == 10.0
        
        # Second is AccuWeather, should be handled failure
        assert results[1].success is False
        assert "Unexpected crash" in results[1].error
