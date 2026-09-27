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
from services.auth import get_current_policyholder
from models.policyholder import Policyholder

router = APIRouter(prefix="/wallets", tags=["Wallets"])


def _paise_to_inr_display(paise: int) -> str:
    return f"₹{paise // 100:,}"


@router.get("/me", response_model=WalletResponse)
async def get_my_wallet(
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> WalletResponse:
    """
    Get the authenticated policyholder's wallet and transactions.
    Wallet is 1:1 with the policyholder.
    """
    wallet = await db.scalar(
        select(Wallet)
        .where(Wallet.policyholder_id == policyholder.id)
        .options(selectinload(Wallet.transactions))
    )
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Wallet not found for this user."},
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
        policyholder_id=str(wallet.policyholder_id),
        balance_paise=wallet.balance_paise,
        balance_inr_display=_paise_to_inr_display(wallet.balance_paise),
        currency=wallet.currency,
        transactions=txs,
    )

