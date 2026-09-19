"""
routers/policies.py — GET /policies/{policy_id}
"""
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.policy import Policy
from schemas.policy import PolicyResponse

router = APIRouter(prefix="/policies", tags=["Policies"])


def _paise_to_inr_display(paise: int) -> str:
    return f"₹{paise // 100:,}"


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
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
        name=policy.name,
        status=policy_status,
        trigger_metric=rule.metric if rule else "rainfall",
        trigger_threshold_mm=rule.threshold_value if rule else 100.0,
        trigger_operator=display_op,
        observation_window_minutes=rule.observation_window_minutes if rule else 60,
        payout_amount_paise=policy.payout_amount_paise,
        payout_amount_inr_display=_paise_to_inr_display(policy.payout_amount_paise),
        currency=policy.currency,
        valid_from=policy.valid_from or getattr(policy, 'start_at', None),
        valid_until=policy.valid_until or getattr(policy, 'end_at', None),
    )

