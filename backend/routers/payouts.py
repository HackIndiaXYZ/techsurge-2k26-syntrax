"""
routers/payouts.py — GET /payouts/{payout_id}
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.payout import Payout
from schemas.payout import PayoutResponse

router = APIRouter(prefix="/payouts", tags=["Payouts"])


def _paise_to_inr_display(paise: int) -> str:
    return f"₹{paise // 100:,}"


@router.get("/{payout_id}", response_model=PayoutResponse)
async def get_payout(
    payout_id: str,
    db: AsyncSession = Depends(get_db),
) -> PayoutResponse:
    payout = await db.get(Payout, payout_id)
    if payout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Payout {payout_id!r} not found."},
        )

    return PayoutResponse(
        payout_id=payout.id,
        policy_id=payout.policy_id,
        trigger_evaluation_id=payout.trigger_evaluation_id,
        status=payout.status.value,
        amount_paise=payout.amount_paise,
        amount_inr_display=_paise_to_inr_display(payout.amount_paise),
        idempotency_key=payout.idempotency_key,
        failure_reason=payout.failure_reason,
        created_at=payout.created_at,
    )

