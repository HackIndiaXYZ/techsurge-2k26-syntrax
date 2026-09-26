"""
models/payment.py — Premium Payment model for Razorpay integration.

Phase 3C: Tracks the lifecycle of a premium payment from order creation
through Razorpay checkout to backend verification and policy activation.

This is the PREMIUM PAYMENT subsystem — completely separate from the
insurance PAYOUT/SETTLEMENT subsystem (wallet, payouts, settlement).
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy import Uuid as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class PaymentStatus(str, enum.Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class PremiumPayment(Base, TimestampMixin):
    """
    Tracks a premium payment for a policy.

    Lifecycle:
        CREATED  → Razorpay order created, awaiting checkout
        PENDING  → Checkout initiated, awaiting verification
        SUCCESS  → Backend verified Razorpay signature, policy activated
        FAILED   → Verification failed or payment cancelled

    Monetary fields are BigInteger paise — NEVER float.
    """
    __tablename__ = "premium_payments"

    __table_args__ = (
        UniqueConstraint("provider_order_id", name="uq_premium_payments_provider_order_id"),
        UniqueConstraint("provider_payment_id", name="uq_premium_payments_provider_payment_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False
    )
    policyholder_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policyholders.id", ondelete="RESTRICT"), nullable=False
    )

    # Amount — integer paise, NEVER float
    amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(Text, default="INR", nullable=False)

    # Provider details
    provider: Mapped[str] = mapped_column(Text, default="razorpay", nullable=False)
    provider_order_id: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    provider_payment_id: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    provider_signature: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(Text, default="CREATED", nullable=False)

    # Timestamps
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    policy: Mapped["Policy"] = relationship("Policy")
    policyholder: Mapped["Policyholder"] = relationship("Policyholder")

    def __repr__(self) -> str:
        return (
            f"<PremiumPayment id={self.id!r} policy={self.policy_id!r} "
            f"status={self.status} amount={self.amount_paise}p>"
        )
