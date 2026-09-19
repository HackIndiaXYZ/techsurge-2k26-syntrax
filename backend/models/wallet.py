"""
models/wallet.py — Wallet and WalletTransaction entities.

Wallet DB columns: id, policy_id, currency, balance_paise, status, created_at, updated_at
WalletTransaction DB columns: id, wallet_id, payout_id, direction, amount_paise,
                               balance_before_paise, balance_after_paise, created_at
"""
import uuid

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class Wallet(Base, TimestampMixin):
    """
    Synthetic wallet holding an integer paise balance.
    balance_paise is BigInteger — never float.
    """
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False
    )
    currency: Mapped[str] = mapped_column(Text, default="INR", nullable=False)
    balance_paise: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    status: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[None] = mapped_column(DateTime(timezone=True), nullable=True)

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
    """
    __tablename__ = "wallet_transactions"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("wallets.id", ondelete="RESTRICT"), nullable=False
    )
    payout_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("payouts.id", ondelete="RESTRICT"), nullable=False
    )

    direction: Mapped[str | None] = mapped_column(Text, nullable=True)

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
