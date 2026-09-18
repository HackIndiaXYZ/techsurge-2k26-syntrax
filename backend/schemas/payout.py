"""
schemas/payout.py — Payout response schema.
"""
from datetime import datetime

from pydantic import BaseModel


class PayoutResponse(BaseModel):
    payout_id: str
    policy_id: str
    trigger_evaluation_id: str
    status: str
    amount_paise: int
    amount_inr_display: str
    idempotency_key: str
    failure_reason: str | None = None
    created_at: datetime

