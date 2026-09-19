"""
schemas/policy.py — Policy response schema.
"""
from datetime import datetime

from pydantic import BaseModel


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

