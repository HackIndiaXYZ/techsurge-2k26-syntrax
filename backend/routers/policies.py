"""
routers/policies.py — GET /policies/{policy_id} and POST /policies

Phase 3B: Added policy creation endpoint with lifecycle management.
"""
import uuid as _uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.policy import Policy, PolicyStatus
from models.region import MicroRegion
from schemas.policy import PolicyCreateRequest, PolicyResponse
from services.auth import get_current_policyholder
from models.policyholder import Policyholder

router = APIRouter(prefix="/policies", tags=["Policies"])


def _paise_to_inr_display(paise: int | None) -> str | None:
    if paise is None:
        return None
    return f"₹{paise // 100:,}"


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> PolicyResponse:
    try:
        pid = _uuid.UUID(policy_id)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": "INVALID_ID", "message": f"Invalid policy_id: {policy_id!r}"})

    policy = await db.scalar(
        select(Policy)
        .where(Policy.id == pid)
        .options(selectinload(Policy.trigger_rule))
    )
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Policy {policy_id!r} not found."},
        )

    # Protect against IDOR
    if policy.policyholder_id != policyholder.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this policy")

    rule = policy.trigger_rule

    # Handle status — may be string or enum depending on model version
    policy_status = policy.status.value if hasattr(policy.status, 'value') else str(policy.status)

    # Map DB operator codes to display symbols
    op_map = {"GTE": ">=", "GT": ">", "LTE": "<=", "LT": "<", "EQ": "=="}
    raw_op = rule.threshold_operator if rule else ">="
    display_op = op_map.get(raw_op, raw_op)

    return PolicyResponse(
        policy_id=str(policy.id),
        region_id=str(policy.region_id),
        name=policy.name or "Unnamed Policy",
        status=policy_status,
        trigger_metric=rule.metric if rule else "rainfall",
        trigger_threshold_mm=rule.threshold_value if rule else 100.0,
        trigger_operator=display_op,
        observation_window_minutes=rule.observation_window_minutes if rule else 60,
        payout_amount_paise=policy.payout_amount_paise,
        payout_amount_inr_display=_paise_to_inr_display(policy.payout_amount_paise),
        currency=policy.currency or "INR",
        valid_from=policy.valid_from or getattr(policy, 'start_at', None),
        valid_until=policy.valid_until or getattr(policy, 'end_at', None),
        premium_amount_paise=policy.premium_amount_paise,
        premium_amount_inr_display=_paise_to_inr_display(policy.premium_amount_paise),
        coverage_amount_paise=policy.coverage_amount_paise,
        coverage_amount_inr_display=_paise_to_inr_display(policy.coverage_amount_paise),
    )


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    request: PolicyCreateRequest,
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> PolicyResponse:
    """
    Create a new policy for the authenticated user.

    The policy is created in PAYMENT_PENDING status.
    Phase 3C (Razorpay TEST) will handle the transition to ACTIVE
    after successful payment verification.

    The caller CANNOT force the status to ACTIVE — that transition
    is reserved for the payment verification pathway.
    """
    # Validate region exists
    try:
        region_uuid = _uuid.UUID(request.region_id)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": "INVALID_ID", "message": f"Invalid region_id: {request.region_id!r}"})

    region = await db.get(MicroRegion, region_uuid)
    if region is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "REGION_NOT_FOUND", "message": f"Region {request.region_id!r} not found."},
        )

    # Validate dates
    if request.end_at <= request.start_at:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "INVALID_DATES", "message": "end_at must be after start_at"},
        )

    # Create policy in PAYMENT_PENDING status
    # The payout_amount_paise mirrors coverage for the settlement engine
    policy = Policy(
        policyholder_id=policyholder.id,
        region_id=region_uuid,
        name=request.name,
        status=PolicyStatus.PAYMENT_PENDING.value,
        premium_amount_paise=request.premium_amount_paise,
        coverage_amount_paise=request.coverage_amount_paise,
        payout_amount_paise=request.coverage_amount_paise,  # settlement engine uses this
        currency=request.currency,
        start_at=request.start_at,
        end_at=request.end_at,
        valid_from=request.start_at,
        valid_until=request.end_at,
    )
    db.add(policy)
    await db.flush()
    await db.refresh(policy)

    return PolicyResponse(
        policy_id=str(policy.id),
        region_id=str(policy.region_id),
        name=policy.name or "Unnamed Policy",
        status=policy.status,
        trigger_metric="rainfall",
        trigger_threshold_mm=100.0,
        trigger_operator=">=",
        observation_window_minutes=60,
        payout_amount_paise=policy.payout_amount_paise,
        payout_amount_inr_display=_paise_to_inr_display(policy.payout_amount_paise),
        currency=policy.currency or "INR",
        valid_from=policy.valid_from,
        valid_until=policy.valid_until,
        premium_amount_paise=policy.premium_amount_paise,
        premium_amount_inr_display=_paise_to_inr_display(policy.premium_amount_paise),
        coverage_amount_paise=policy.coverage_amount_paise,
        coverage_amount_inr_display=_paise_to_inr_display(policy.coverage_amount_paise),
    )
