"""
schemas/common.py — Shared response schemas.
"""
from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict[str, Any] = {}


class HealthResponse(BaseModel):
    status: str          # "ok" | "degraded"
    environment: str
    database: str        # "connected" | "error"

