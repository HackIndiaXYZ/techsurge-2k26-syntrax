"""
models/payout.py — Payout entity.

Records a payout attempt.

DB columns: id, policy_id, trigger_evaluation_id, wallet_id, amount_paise,
            status, idempotency_scope, idempotency_key, provider_name,
            provider_reference, initiated_at, completed_at, created_at,
            updated_at, failure_reason
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text
from sqlalchemy import Uuid as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class PayoutStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payout(Base, TimestampMixin):
    """
    A synthetic payout record.
    amount_paise is BigInteger — NEVER float.
    """
    __tablename__ = "payouts"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    policy_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False
    )
    trigger_evaluation_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("trigger_evaluations.id", ondelete="RESTRICT"), nullable=False
    )
    wallet_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("wallets.id", ondelete="SET NULL"), nullable=True
    )

    # Amount in integer paise — ₹10,000 = 1,000,000 paise
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)

    status: Mapped[str] = mapped_column(Text, default="PENDING", nullable=False)

    idempotency_scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    provider_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    initiated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    policy: Mapped["Policy"] = relationship("Policy", back_populates="payouts")
    trigger_evaluation: Mapped["TriggerEvaluation"] = relationship(
        "TriggerEvaluation", back_populates="payout"
    )
    wallet_transaction: Mapped["WalletTransaction"] = relationship(
        "WalletTransaction", back_populates="payout", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Payout id={self.id!r} status={self.status} amount={self.amount_paise}p>"
