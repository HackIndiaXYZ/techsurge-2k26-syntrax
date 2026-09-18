"""
routers/policies.py — GET /policies/{policy_id}
"""
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
    policy = await db.scalar(
        select(Policy)
        .where(Policy.id == policy_id)
        .options(selectinload(Policy.trigger_rule))
    )
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Policy {policy_id!r} not found."},
        )

    rule = policy.trigger_rule
    return PolicyResponse(
        policy_id=policy.id,
        region_id=policy.region_id,
        name=policy.name,
        status=policy.status.value,
        trigger_metric=rule.metric if rule else "rainfall",
        trigger_threshold_mm=rule.threshold_value if rule else 100.0,
        trigger_operator=rule.threshold_operator if rule else ">=",
        observation_window_minutes=rule.observation_window_minutes if rule else 60,
        payout_amount_paise=policy.payout_amount_paise,
        payout_amount_inr_display=_paise_to_inr_display(policy.payout_amount_paise),
        currency=policy.currency,
        valid_from=policy.valid_from,
        valid_until=policy.valid_until,
    )

