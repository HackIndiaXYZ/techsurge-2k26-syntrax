import httpx
import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Tuple

from .base import WeatherProvider, CanonicalWeatherObservation, ProviderFetchResult, ProviderStatus

logger = logging.getLogger(__name__)

class AccuWeatherProvider(WeatherProvider):
    def __init__(self, api_key: str, base_url: str = "http://dataservice.accuweather.com", timeout_seconds: int = 10):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self._location_cache: Dict[Tuple[float, float], str] = {}

    @property
    def name(self) -> str:
        return "AccuWeather"

    async def _get_location_key(self, client: httpx.AsyncClient, lat: float, lon: float) -> Optional[str]:
        cache_key = (round(lat, 2), round(lon, 2))
        if cache_key in self._location_cache:
            return self._location_cache[cache_key]

        url = f"{self.base_url}/locations/v1/cities/geoposition/search"
        params = {"apikey": self.api_key, "q": f"{lat},{lon}"}
        
        response = await client.get(url, params=params, timeout=self.timeout_seconds)
        response.raise_for_status()
        
        data = response.json()
        if data and "Key" in data:
            location_key = data["Key"]
            self._location_cache[cache_key] = location_key
            return location_key
        return None

    async def fetch_current(self, latitude: float, longitude: float) -> ProviderFetchResult:
        start_time = time.monotonic()
        
        if not self.api_key:
            return self._error_result(ProviderStatus.UNAVAILABLE, "API key not configured", start_time)

        for attempt in range(3):
            try:
                async with httpx.AsyncClient() as client:
                    location_key = await self._get_location_key(client, latitude, longitude)
                    if not location_key:
                        return self._error_result(ProviderStatus.BAD_RESPONSE, "Failed to resolve location key", start_time)

                    url = f"{self.base_url}/currentconditions/v1/{location_key}"
                    params = {"apikey": self.api_key, "details": "true"}
                    
                    response = await client.get(url, params=params, timeout=self.timeout_seconds)
                    response.raise_for_status()
                    
                    data = response.json()
                    if not data:
                        return self._error_result(ProviderStatus.NO_DATA, "Empty response", start_time)
                        
                    current = data[0]
                    
                    observed_at_str = current.get("LocalObservationDateTime")
                    observed_at = datetime.fromisoformat(observed_at_str).astimezone(timezone.utc) if observed_at_str else datetime.now(timezone.utc)
                    
                    precip = current.get("Precip1hr", {}).get("Metric", {}).get("Value")
                    temp = current.get("Temperature", {}).get("Metric", {}).get("Value")
                    humidity = current.get("RelativeHumidity")
                    wind = current.get("Wind", {}).get("Speed", {}).get("Metric", {}).get("Value")
                    pressure = current.get("Pressure", {}).get("Metric", {}).get("Value")

                    observation = CanonicalWeatherObservation(
                        source_id="accuweather",
                        source_name=self.name,
                        latitude=latitude,
                        longitude=longitude,
                        observed_at=observed_at,
                        received_at=datetime.now(timezone.utc),
                        rainfall_1h_mm=precip,
                        temperature_c=temp,
                        humidity_percent=humidity,
                        wind_speed_kmh=wind,
                        pressure_hpa=pressure,
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
                status = e.response.status_code
                if status in (401, 403):
                    return self._error_result(ProviderStatus.AUTH_ERROR, f"Auth Error {status}", start_time)
                elif status == 429:
                    return self._error_result(ProviderStatus.RATE_LIMITED, "Rate Limited", start_time)
                return self._error_result(ProviderStatus.SERVER_ERROR, f"HTTP Error {status}", start_time)
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
        if not self.api_key:
            return ProviderStatus.UNAVAILABLE
        res = await self.fetch_current(52.52, 13.41)
        return ProviderStatus.ONLINE if res.success else ProviderStatus.OFFLINE

