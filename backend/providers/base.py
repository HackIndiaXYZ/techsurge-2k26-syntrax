import enum
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class ProviderStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    SERVER_ERROR = "SERVER_ERROR"
    BAD_RESPONSE = "BAD_RESPONSE"
    STALE_DATA = "STALE_DATA"
    NO_DATA = "NO_DATA"

class CanonicalWeatherObservation(BaseModel):
    source_id: str
    source_name: str
    latitude: float
    longitude: float
    observed_at: datetime
    received_at: datetime
    rainfall_1h_mm: Optional[float]
    rainfall_accumulation_window_minutes: int = 60
    temperature_c: Optional[float]
    humidity_percent: Optional[float]
    wind_speed_kmh: Optional[float]
    pressure_hpa: Optional[float]
    source_status: ProviderStatus
    raw_payload_reference: Optional[str] = None
    quality_status: str = "PENDING"
    provider_request_id: Optional[str] = None

class ProviderFetchResult(BaseModel):
    success: bool
    observation: Optional[CanonicalWeatherObservation]
    error: Optional[str]
    error_type: Optional[ProviderStatus]
    latency_ms: int
    provider_name: str

class WeatherProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def fetch_current(self, latitude: float, longitude: float) -> ProviderFetchResult:
        pass

    @abstractmethod
    async def health_check(self) -> ProviderStatus:
        pass

