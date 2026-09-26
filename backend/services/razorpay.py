"""
services/razorpay.py — Razorpay TEST client wrapper.

Phase 3C: Encapsulates all Razorpay API interactions.
The secret key NEVER leaves this module.
"""
import hmac
import hashlib
import logging

import razorpay
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_razorpay_client() -> razorpay.Client:
    """
    Returns a configured Razorpay client using TEST credentials.
    Raises ValueError if credentials are not configured.
    """
    key_id = settings.razorpay_key_id
    key_secret = settings.razorpay_key_secret

    if not key_id or not key_secret:
        raise ValueError(
            "Razorpay credentials not configured. "
            "Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in environment."
        )

    return razorpay.Client(auth=(key_id, key_secret))


def create_order(amount_paise: int, currency: str = "INR", receipt: str = "") -> dict:
    """
    Create a Razorpay TEST order.

    Args:
        amount_paise: Amount in paise (integer). Razorpay expects this as 'amount'.
        currency: Currency code (default INR).
        receipt: Optional receipt identifier for tracking.

    Returns:
        Razorpay order dict containing 'id', 'amount', 'currency', 'status', etc.
    """
    client = get_razorpay_client()
    order_data = {
        "amount": amount_paise,  # Razorpay uses paise natively
        "currency": currency,
        "receipt": receipt,
    }
    order = client.order.create(data=order_data)
    logger.info(f"Razorpay TEST order created: {order.get('id')} amount={amount_paise}p")
    return order


def verify_payment_signature(
    order_id: str,
    payment_id: str,
    signature: str,
) -> bool:
    """
    Verify Razorpay payment signature using HMAC-SHA256.

    The expected signature is:
        HMAC-SHA256(order_id + "|" + payment_id, key_secret)

    Returns True if valid, False otherwise.
    Never logs the secret or full signature.
    """
    key_secret = settings.razorpay_key_secret
    if not key_secret:
        logger.error("RAZORPAY_KEY_SECRET not configured — cannot verify signature")
        return False

    message = f"{order_id}|{payment_id}"
    expected_signature = hmac.new(
        key_secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    is_valid = hmac.compare_digest(expected_signature, signature)

    if not is_valid:
        logger.warning(f"Razorpay signature verification FAILED for order={order_id}")
    else:
        logger.info(f"Razorpay signature verified for order={order_id}")

    return is_valid
