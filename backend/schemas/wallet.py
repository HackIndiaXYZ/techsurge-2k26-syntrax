"""
schemas/wallet.py — Wallet and WalletTransaction response schemas.
"""
from datetime import datetime

from pydantic import BaseModel


class WalletTransactionResponse(BaseModel):
    transaction_id: str
    payout_id: str
    amount_paise: int
    balance_before_paise: int
    balance_after_paise: int
    created_at: datetime


class WalletResponse(BaseModel):
    wallet_id: str
    policy_id: str
    balance_paise: int
    balance_inr_display: str
    currency: str
    transactions: list[WalletTransactionResponse] = []

