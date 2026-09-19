"""
schemas/telemetry.py — Telemetry ingestion request/response schemas.
"""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TelemetryIngestRequest(BaseModel):
    """
    A single rainfall telemetry observation submitted to POST /telemetry.

    Rules enforced here (application-level):
    - metric must be "rainfall"
    - unit must be "mm"
    - value must be >= 0
    - event_id, source_id, region_id must be non-empty strings
    - observed_at must be a valid datetime
    """
    event_id: str = Field(..., min_length=1, max_length=128, description="Client-generated unique event ID")
    source_id: str = Field(..., min_length=1, max_length=64)
    region_id: str = Field(..., min_length=1, max_length=64)
    observed_at: datetime = Field(..., description="When the measurement was taken (UTC)")
    metric: str = Field(..., description="Must be 'rainfall' for PS-F03")
    value: float = Field(..., description="Rainfall value in mm. Must be >= 0.")
    unit: str = Field(..., description="Must be 'mm'")

    @field_validator("metric")
    @classmethod
    def metric_must_be_rainfall(cls, v: str) -> str:
        if v.lower() != "rainfall":
            raise ValueError(f"Unsupported metric '{v}'. Only 'rainfall' is accepted.")
        return v.lower()

    @field_validator("unit")
    @classmethod
    def unit_must_be_mm(cls, v: str) -> str:
        if v.lower() != "mm":
            raise ValueError(f"Unsupported unit '{v}'. Only 'mm' is accepted.")
        return v.lower()

    @field_validator("value")
    @classmethod
    def value_must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"Rainfall value must be >= 0. Got {v}.")
        return v


class TelemetryIngestResponse(BaseModel):
    status: str                  # "ACCEPTED" | "DUPLICATE"
    event_id: str
    correlation_id: str
    received_at: datetime
    message: str | None = None

