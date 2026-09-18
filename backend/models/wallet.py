"""
models/wallet.py — Wallet and WalletTransaction entities.

SYNTHETIC WALLET — no real money, no real bank, no UPI.

Wallet.balance_paise is the authoritative current balance.
Every change is recorded as a WalletTransaction row (append-only ledger).

MONETARY RULE: All amounts are integer paise. NEVER float.
"""
from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class Wallet(Base, TimestampMixin):
    """
    Synthetic wallet holding an integer paise balance.
    One wallet per policy for the PS-F03 demo.
    balance_paise is BigInteger — never float.
    """
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)   # human-readable ID
    policy_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    # Current balance — BigInteger, integer paise only
    balance_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    # Relationships
    policy: Mapped["Policy"] = relationship("Policy", back_populates="wallets")
    transactions: Mapped[list["WalletTransaction"]] = relationship(
        "WalletTransaction", back_populates="wallet", order_by="WalletTransaction.created_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<Wallet id={self.id!r} balance={self.balance_paise}p>"


class WalletTransaction(Base, TimestampMixin):
    """
    An immutable ledger entry recording a wallet balance change.

    balance_before_paise + amount_paise == balance_after_paise (always)
    Linked 1:1 to a Payout via payout_id (unique constraint prevents double-credit).
    """
    __tablename__ = "wallet_transactions"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)

    wallet_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("wallets.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # One WalletTransaction per Payout — prevents double-credit at DB level
    payout_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("payouts.id", ondelete="RESTRICT"), nullable=False, unique=True
    )

    # All amounts are BigInteger — NEVER float
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_before_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_after_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Relationships
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="transactions")
    payout: Mapped["Payout"] = relationship("Payout", back_populates="wallet_transaction")

    def __repr__(self) -> str:
        return (
            f"<WalletTransaction id={self.id!r} "
            f"amount={self.amount_paise}p "
            f"before={self.balance_before_paise}p after={self.balance_after_paise}p>"
        )

