"""
schemas/payment.py — Payment request/response schemas.

Phase 3C: Razorpay TEST payment integration schemas.
"""
from datetime import datetime

from pydantic import BaseModel


class PaymentOrderResponse(BaseModel):
    """
    Returned to the frontend after creating a Razorpay TEST order.
    Contains ONLY the data needed for Razorpay Checkout.
    The secret key is NEVER included.
    """
    payment_id: str          # Internal PremiumPayment UUID
    policy_id: str
    razorpay_order_id: str
    razorpay_key_id: str     # Public key only — safe for frontend
    amount_paise: int
    currency: str
    status: str


class PaymentVerifyRequest(BaseModel):
    """
    Frontend sends Razorpay checkout result for backend verification.
    The backend independently verifies the cryptographic signature.
    """
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentVerifyResponse(BaseModel):
    """
    Backend verification result.
    """
    payment_id: str
    policy_id: str
    payment_status: str
    policy_status: str
    verified: bool


class PaymentStatusResponse(BaseModel):
    """
    Payment status for a policy.
    """
    payment_id: str
    policy_id: str
    amount_paise: int
    currency: str
    status: str
    provider_order_id: str | None = None
    created_at: datetime
    verified_at: datetime | None = None
