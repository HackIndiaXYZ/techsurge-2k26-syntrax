"""
schemas/policy.py — Policy request/response schemas.

Phase 3B: Added PolicyCreateRequest for policy lifecycle management.
"""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PolicyCreateRequest(BaseModel):
    """
    Request body for POST /policies.
    Creates a new policy in PAYMENT_PENDING status.
    Phase 3C will handle actual payment to transition to ACTIVE.
    """
    region_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    premium_amount_paise: int = Field(..., gt=0, description="Premium amount in paise (integer)")
    coverage_amount_paise: int = Field(..., gt=0, description="Coverage/payout amount in paise (integer)")
    currency: str = Field(default="INR", max_length=10)
    start_at: datetime = Field(..., description="Policy coverage start (UTC)")
    end_at: datetime = Field(..., description="Policy coverage end (UTC)")

    @field_validator("premium_amount_paise", "coverage_amount_paise")
    @classmethod
    def validate_paise_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Monetary values must be positive integers (paise)")
        return v

    @field_validator("end_at")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info) -> datetime:
        start = info.data.get("start_at")
        if start and v <= start:
            raise ValueError("end_at must be after start_at")
        return v


class PolicyResponse(BaseModel):
    policy_id: str
    region_id: str
    name: str
    status: str
    trigger_metric: str
    trigger_threshold_mm: float
    trigger_operator: str
    observation_window_minutes: int
    payout_amount_paise: int
    payout_amount_inr_display: str
    currency: str
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    # Phase 3B fields
    premium_amount_paise: int | None = None
    premium_amount_inr_display: str | None = None
    coverage_amount_paise: int | None = None
    coverage_amount_inr_display: str | None = None

