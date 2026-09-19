import asyncio
from typing import List
import logging

from .base import WeatherProvider, ProviderFetchResult
from .openmeteo import OpenMeteoProvider
from .accuweather import AccuWeatherProvider
from .imd import IMDProvider

logger = logging.getLogger(__name__)

class ProviderRegistry:
    def __init__(self):
        self._providers: List[WeatherProvider] = []
        self._provider_map = {}

    def register(self, provider: WeatherProvider):
        self._providers.append(provider)
        self._provider_map[provider.name.lower()] = provider
        logger.info(f"Registered weather provider: {provider.name}")

    def get_provider(self, name: str) -> WeatherProvider:
        return self._provider_map.get(name.lower())

    def list_providers(self) -> List[str]:
        return [p.name for p in self._providers]

    async def fetch_all(self, latitude: float, longitude: float) -> List[ProviderFetchResult]:
        tasks = [
            provider.fetch_current(latitude, longitude)
            for provider in self._providers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for p, result in zip(self._providers, results):
            if isinstance(result, Exception):
                logger.error(f"Provider {p.name} threw an unhandled exception: {result}")
                # We construct a failed ProviderFetchResult to maintain consistent output type
                valid_results.append(
                    ProviderFetchResult(
                        success=False,
                        observation=None,
                        error=str(result),
                        error_type=None,
                        latency_ms=0,
                        provider_name=p.name
                    )
                )
            else:
                valid_results.append(result)
                
        return valid_results

