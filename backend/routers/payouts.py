"""
routers/payouts.py — GET /payouts/{payout_id}
"""
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.payout import Payout
from schemas.payout import PayoutResponse
from services.auth import get_current_policyholder
from models.policyholder import Policyholder
from sqlalchemy.orm import selectinload
from sqlalchemy import select

router = APIRouter(prefix="/payouts", tags=["Payouts"])


def _paise_to_inr_display(paise: int) -> str:
    return f"₹{paise // 100:,}"


@router.get("/{payout_id}", response_model=PayoutResponse)
async def get_payout(
    payout_id: str,
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> PayoutResponse:
    try:
        pid = _uuid.UUID(payout_id)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": "INVALID_ID", "message": f"Invalid payout_id: {payout_id!r}"})

    payout = await db.scalar(
        select(Payout).where(Payout.id == pid).options(selectinload(Payout.policy))
    )
    if payout is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Payout {payout_id!r} not found."},
        )

    if not payout.policy or payout.policy.policyholder_id != policyholder.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this payout")

    return PayoutResponse(
        payout_id=str(payout.id),
        policy_id=str(payout.policy_id),
        trigger_evaluation_id=str(payout.trigger_evaluation_id) if payout.trigger_evaluation_id else None,
        status=payout.status.value if hasattr(payout.status, 'value') else str(payout.status),
        amount_paise=payout.amount_paise,
        amount_inr_display=_paise_to_inr_display(payout.amount_paise),
        idempotency_key=str(payout.idempotency_key) if payout.idempotency_key else None,
        failure_reason=payout.failure_reason,
        created_at=payout.created_at,
    )

