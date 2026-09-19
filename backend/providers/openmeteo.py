import httpx
import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Optional

from .base import WeatherProvider, CanonicalWeatherObservation, ProviderFetchResult, ProviderStatus

logger = logging.getLogger(__name__)

class OpenMeteoProvider(WeatherProvider):
    def __init__(self, base_url: str = "https://api.open-meteo.com", timeout_seconds: int = 10):
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "OpenMeteo"

    async def fetch_current(self, latitude: float, longitude: float) -> ProviderFetchResult:
        start_time = time.monotonic()
        url = f"{self.base_url}/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "rain,temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure",
            "timezone": "UTC"
        }

        for attempt in range(3):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=self.timeout_seconds)
                    response.raise_for_status()
                    
                    data = response.json()
                    current = data.get("current", {})
                    
                    observed_at = datetime.fromisoformat(current.get("time").replace("Z", "+00:00")).replace(tzinfo=timezone.utc)
                    
                    observation = CanonicalWeatherObservation(
                        source_id="openmeteo",
                        source_name=self.name,
                        latitude=latitude,
                        longitude=longitude,
                        observed_at=observed_at,
                        received_at=datetime.now(timezone.utc),
                        rainfall_1h_mm=current.get("rain"),
                        temperature_c=current.get("temperature_2m"),
                        humidity_percent=current.get("relative_humidity_2m"),
                        wind_speed_kmh=current.get("wind_speed_10m"),
                        pressure_hpa=current.get("surface_pressure"),
                        source_status=ProviderStatus.ONLINE
                    )
                    
                    latency_ms = int((time.monotonic() - start_time) * 1000)
                    return ProviderFetchResult(
                        success=True,
                        observation=observation,
                        error=None,
                        error_type=None,
                        latency_ms=latency_ms,
                        provider_name=self.name
                    )

            except httpx.TimeoutException:
                if attempt == 2:
                    return self._error_result(ProviderStatus.TIMEOUT, "Request timed out", start_time)
            except httpx.HTTPStatusError as e:
                return self._error_result(ProviderStatus.SERVER_ERROR, f"HTTP Error {e.response.status_code}", start_time)
            except Exception as e:
                return self._error_result(ProviderStatus.UNKNOWN, str(e), start_time)
                
            await asyncio.sleep(2 ** attempt)

        return self._error_result(ProviderStatus.UNKNOWN, "Max retries exceeded", start_time)

    def _error_result(self, error_type: ProviderStatus, error_msg: str, start_time: float) -> ProviderFetchResult:
        latency_ms = int((time.monotonic() - start_time) * 1000)
        return ProviderFetchResult(
            success=False,
            observation=None,
            error=error_msg,
            error_type=error_type,
            latency_ms=latency_ms,
            provider_name=self.name
        )

    async def health_check(self) -> ProviderStatus:
        res = await self.fetch_current(52.52, 13.41)
        return ProviderStatus.ONLINE if res.success else ProviderStatus.OFFLINE

