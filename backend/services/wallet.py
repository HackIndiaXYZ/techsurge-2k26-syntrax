"""
services/wallet.py — Synthetic wallet credit service.

Rules:
- balance_paise is always an integer. NEVER float.
- One WalletTransaction per Payout (unique constraint on payout_id).
- balance_after = balance_before + amount (atomic, in the same DB transaction).
- Wallet credit is always part of the settlement transaction — NOT a separate commit.
"""
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.wallet import Wallet, WalletTransaction
from models.audit import AuditEventType
from services.audit import write_audit_event
from services.ids import new_uuid


async def credit_wallet(
    policy_id: str,
    payout_id: str,
    amount_paise: int,   # MUST be integer — callers must not pass float
    correlation_id: str,
    db: AsyncSession,
) -> WalletTransaction:
    """
    Credit the synthetic wallet for the given policy.

    Atomically:
      1. Fetch the wallet row.
      2. Compute balance_before and balance_after.
      3. Update wallet.balance_paise.
      4. Insert WalletTransaction row.
      5. Write audit event.

    All in the same DB transaction — caller commits.

    Raises:
      ValueError: if no wallet found for the policy.
    """
    assert isinstance(amount_paise, int), (
        f"amount_paise must be int, got {type(amount_paise).__name__}: {amount_paise}"
    )

    # ── Fetch wallet ─────────────────────────────────────────────────────────
    wallet = await db.scalar(
        select(Wallet).where(Wallet.policy_id == policy_id).with_for_update()
    )
    if wallet is None:
        raise ValueError(f"No wallet found for policy_id={policy_id!r}")

    balance_before: int = wallet.balance_paise  # integer
    balance_after: int = balance_before + amount_paise  # integer arithmetic only

    # Sanity assertion — no float contamination
    assert isinstance(balance_before, int), "balance_before must be int"
    assert isinstance(balance_after, int), "balance_after must be int"

    # ── Update wallet balance ────────────────────────────────────────────────
    wallet.balance_paise = balance_after
    await db.flush()

    # ── Insert ledger transaction ─────────────────────────────────────────────
    tx = WalletTransaction(
        id=new_uuid(),
        wallet_id=wallet.id,
        payout_id=payout_id,
        direction="CREDIT",
        amount_paise=amount_paise,
        balance_before_paise=balance_before,
        balance_after_paise=balance_after,
    )
    db.add(tx)
    await db.flush()

    # ── Audit ────────────────────────────────────────────────────────────────
    await write_audit_event(
        db=db,
        event_type=AuditEventType.WALLET_CREDITED,
        entity_type="WALLET",
        entity_id=str(wallet.id),
        policy_id=policy_id,
        correlation_id=correlation_id,
        status="SUCCESS",
        message=(
            f"Wallet credited {amount_paise} paise. "
            f"Balance: {balance_before} → {balance_after} paise."
        ),
        metadata={
            "wallet_id": str(wallet.id),
            "payout_id": str(payout_id),
            "amount_paise": amount_paise,
            "balance_before_paise": balance_before,
            "balance_after_paise": balance_after,
        },
    )

    return tx

