"""
models/payout.py — Payout entity.

Records a payout attempt.

IDEMPOTENCY GUARANTEE:
  UniqueConstraint("policy_id", "trigger_evaluation_id") at the database level
  ensures that the same qualifying event can only produce ONE payout record,
  even under concurrent requests.

  Duplicate INSERT raises IntegrityError → caught by settlement service →
  returns ALREADY_SETTLED without double-crediting the wallet.
"""
import enum

from sqlalchemy import BigInteger, Enum, ForeignKey, String, UniqueConstraint
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
    Idempotency is enforced by the unique constraint on (policy_id, trigger_evaluation_id).
    """
    __tablename__ = "payouts"
    __table_args__ = (
        UniqueConstraint(
            "policy_id",
            "trigger_evaluation_id",
            name="uq_payout_policy_trigger",
        ),
    )

    id: Mapped[str] = mapped_column(String(26), primary_key=True)

    policy_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    trigger_evaluation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("trigger_evaluations.id", ondelete="RESTRICT"), nullable=False
    )

    status: Mapped[PayoutStatus] = mapped_column(
        Enum(PayoutStatus), default=PayoutStatus.PENDING, nullable=False
    )

    # Amount in integer paise — ₹10,000 = 1,000,000 paise
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Human-readable idempotency key for logging/tracing
    idempotency_key: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    failure_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Provider reference returned by the payout provider (synthetic for mock, real txn ID for live)
    # NOTE: Requires DB migration when applied to existing PostgreSQL instance.
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

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

