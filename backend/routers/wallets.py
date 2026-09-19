"""
routers/wallets.py — GET /wallets/{wallet_id}
"""
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.wallet import Wallet, WalletTransaction
from schemas.wallet import WalletResponse, WalletTransactionResponse

router = APIRouter(prefix="/wallets", tags=["Wallets"])


def _paise_to_inr_display(paise: int) -> str:
    return f"₹{paise // 100:,}"


@router.get("/{wallet_id}", response_model=WalletResponse)
async def get_wallet(
    wallet_id: str,
    db: AsyncSession = Depends(get_db),
) -> WalletResponse:
    try:
        wid = _uuid.UUID(wallet_id)
    except ValueError:
        raise HTTPException(status_code=400, detail={"error": "INVALID_ID", "message": f"Invalid wallet_id: {wallet_id!r}"})

    wallet = await db.scalar(
        select(Wallet)
        .where(Wallet.id == wid)
        .options(selectinload(Wallet.transactions))
    )
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Wallet {wallet_id!r} not found."},
        )

    txs = [
        WalletTransactionResponse(
            transaction_id=str(tx.id),
            payout_id=str(tx.payout_id),
            amount_paise=tx.amount_paise,
            balance_before_paise=tx.balance_before_paise,
            balance_after_paise=tx.balance_after_paise,
            created_at=tx.created_at,
        )
        for tx in wallet.transactions
    ]

    return WalletResponse(
        wallet_id=str(wallet.id),
        policy_id=str(wallet.policy_id),
        balance_paise=wallet.balance_paise,
        balance_inr_display=_paise_to_inr_display(wallet.balance_paise),
        currency=wallet.currency,
        transactions=txs,
    )

