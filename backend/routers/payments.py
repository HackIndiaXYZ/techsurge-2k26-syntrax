"""
routers/payments.py — Premium payment endpoints.

Phase 3C: Razorpay TEST payment integration.

Endpoints:
    POST /policies/{policy_id}/payments/order   — Create Razorpay TEST order
    POST /policies/{policy_id}/payments/verify   — Verify payment & activate policy
    GET  /policies/{policy_id}/payments/status   — Get payment status

SECURITY INVARIANTS:
    - Amount comes from server-side Policy.premium_amount_paise, NEVER frontend
    - Policy activation happens ONLY after backend signature verification
    - All endpoints require JWT-derived policyholder ownership
    - Razorpay secret key NEVER reaches the frontend
"""
import uuid as _uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database import get_db
from models.payment import PaymentStatus, PremiumPayment
from models.policy import Policy, PolicyStatus
from models.policyholder import Policyholder
from schemas.payment import (
    PaymentOrderResponse,
    PaymentStatusResponse,
    PaymentVerifyRequest,
    PaymentVerifyResponse,
)
from services.auth import get_current_policyholder
from services import razorpay as razorpay_service

settings = get_settings()
router = APIRouter(prefix="/policies", tags=["Payments"])


async def _get_owned_policy(
    policy_id: str,
    db: AsyncSession,
    policyholder: Policyholder,
) -> Policy:
    """Retrieve a policy and verify JWT-derived ownership."""
    try:
        pid = _uuid.UUID(policy_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_ID", "message": f"Invalid policy_id: {policy_id!r}"},
        )

    policy = await db.get(Policy, pid)
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Policy {policy_id!r} not found."},
        )

    if policy.policyholder_id != policyholder.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this policy")

    return policy


@router.post(
    "/{policy_id}/payments/order",
    response_model=PaymentOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment_order(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> PaymentOrderResponse:
    """
    Create a Razorpay TEST order for an authenticated user's policy premium.

    SECURITY:
    - Amount comes from Policy.premium_amount_paise (server-side), NOT frontend.
    - Only PAYMENT_PENDING policies can initiate payment.
    - Duplicate order protection: reuses existing CREATED payment if present.
    """
    policy = await _get_owned_policy(policy_id, db, policyholder)

    # Only PAYMENT_PENDING policies can initiate payment
    if policy.status != PolicyStatus.PAYMENT_PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "INVALID_STATE",
                "message": f"Policy status is {policy.status!r} — only PAYMENT_PENDING policies can initiate payment.",
            },
        )

    if not policy.premium_amount_paise or policy.premium_amount_paise <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "NO_PREMIUM", "message": "Policy has no valid premium amount."},
        )

    # Duplicate order protection: check for existing CREATED payment
    existing = await db.scalar(
        select(PremiumPayment)
        .where(PremiumPayment.policy_id == policy.id)
        .where(PremiumPayment.status == PaymentStatus.CREATED.value)
    )
    if existing and existing.provider_order_id:
        # Reuse existing order
        return PaymentOrderResponse(
            payment_id=str(existing.id),
            policy_id=str(policy.id),
            razorpay_order_id=existing.provider_order_id,
            razorpay_key_id=settings.razorpay_key_id,
            amount_paise=existing.amount_paise,
            currency=existing.currency,
            status=existing.status,
        )

    # Create Razorpay TEST order — amount from server-side policy premium
    amount = policy.premium_amount_paise
    currency = policy.currency or "INR"
    receipt = f"policy-{policy.id}"

    try:
        rz_order = razorpay_service.create_order(
            amount_paise=amount,
            currency=currency,
            receipt=receipt,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": "PAYMENT_UNAVAILABLE", "message": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "PAYMENT_PROVIDER_ERROR", "message": f"Failed to create order: {e}"},
        )

    # Create payment record
    payment = PremiumPayment(
        policy_id=policy.id,
        policyholder_id=policyholder.id,
        amount_paise=amount,
        currency=currency,
        provider="razorpay",
        provider_order_id=rz_order["id"],
        status=PaymentStatus.CREATED.value,
    )
    db.add(payment)
    await db.flush()
    await db.refresh(payment)

    return PaymentOrderResponse(
        payment_id=str(payment.id),
        policy_id=str(policy.id),
        razorpay_order_id=rz_order["id"],
        razorpay_key_id=settings.razorpay_key_id,  # Public key only
        amount_paise=amount,
        currency=currency,
        status=payment.status,
    )


@router.post(
    "/{policy_id}/payments/verify",
    response_model=PaymentVerifyResponse,
)
async def verify_payment(
    policy_id: str,
    request: PaymentVerifyRequest,
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> PaymentVerifyResponse:
    """
    Verify Razorpay payment signature and activate policy.

    SECURITY INVARIANTS:
    - Backend independently verifies cryptographic signature
    - Frontend "success" is NEVER trusted
    - Policy activation happens ONLY inside this verified path
    - Idempotent: repeated verification of same payment returns same result
    """
    policy = await _get_owned_policy(policy_id, db, policyholder)

    # Find the payment record by order ID
    payment = await db.scalar(
        select(PremiumPayment)
        .where(PremiumPayment.provider_order_id == request.razorpay_order_id)
        .where(PremiumPayment.policy_id == policy.id)
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "PAYMENT_NOT_FOUND", "message": "No payment found for this order."},
        )

    # Idempotency: if already verified successfully, return existing result
    if payment.status == PaymentStatus.SUCCESS.value:
        return PaymentVerifyResponse(
            payment_id=str(payment.id),
            policy_id=str(policy.id),
            payment_status=payment.status,
            policy_status=policy.status,
            verified=True,
        )

    # Verify Razorpay signature
    is_valid = razorpay_service.verify_payment_signature(
        order_id=request.razorpay_order_id,
        payment_id=request.razorpay_payment_id,
        signature=request.razorpay_signature,
    )

    if not is_valid:
        # Mark payment as FAILED — do NOT activate policy
        payment.status = PaymentStatus.FAILED.value
        payment.updated_at = datetime.now(timezone.utc)
        await db.flush()

        return PaymentVerifyResponse(
            payment_id=str(payment.id),
            policy_id=str(policy.id),
            payment_status=payment.status,
            policy_status=policy.status,
            verified=False,
        )

    # === CRITICAL: Transactional policy activation ===
    # Signature verified → update payment AND policy atomically
    now = datetime.now(timezone.utc)

    payment.status = PaymentStatus.SUCCESS.value
    payment.provider_payment_id = request.razorpay_payment_id
    payment.provider_signature = request.razorpay_signature
    payment.verified_at = now
    payment.updated_at = now

    # Activate policy ONLY if still PAYMENT_PENDING
    if policy.status == PolicyStatus.PAYMENT_PENDING.value:
        policy.status = PolicyStatus.ACTIVE.value
        policy.updated_at = now

    await db.flush()

    return PaymentVerifyResponse(
        payment_id=str(payment.id),
        policy_id=str(policy.id),
        payment_status=payment.status,
        policy_status=policy.status,
        verified=True,
    )


@router.get(
    "/{policy_id}/payments/status",
    response_model=PaymentStatusResponse,
)
async def get_payment_status(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> PaymentStatusResponse:
    """Get the latest payment status for a policy."""
    policy = await _get_owned_policy(policy_id, db, policyholder)

    payment = await db.scalar(
        select(PremiumPayment)
        .where(PremiumPayment.policy_id == policy.id)
        .order_by(PremiumPayment.created_at.desc())
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NO_PAYMENT", "message": "No payment found for this policy."},
        )

    return PaymentStatusResponse(
        payment_id=str(payment.id),
        policy_id=str(policy.id),
        amount_paise=payment.amount_paise,
        currency=payment.currency,
        status=payment.status,
        provider_order_id=payment.provider_order_id,
        created_at=payment.created_at,
        verified_at=payment.verified_at,
    )
