"""
models/policy.py — Policy and TriggerRule entities.

Policy encapsulates the parametric insurance contract.
TriggerRule defines the conditions under which a payout fires.

For PS-F03 demo:
  One policy: policy-kaveri-2026
  One rule: rainfall >= 100 mm within 60 minutes
  Payout: 1,000,000 paise (₹10,000)
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, Numeric, Text
from sqlalchemy import Uuid as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class PolicyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"


class Policy(Base, TimestampMixin):
    """
    A parametric insurance policy.
    Monetary field (payout_amount_paise) is BigInteger — integer only, never float.
    
    DB columns: id, policyholder_id, region_id, trigger_rule_id, payout_amount_paise,
                status, start_at, end_at, created_at, updated_at, name, currency,
                valid_from, valid_until
    """
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policyholder_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policyholders.id", ondelete="RESTRICT"), nullable=True
    )
    region_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False
    )
    trigger_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("trigger_rules.id", ondelete="SET NULL"), nullable=True
    )

    # Payout — stored as integer paise (NEVER float)
    payout_amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)

    status: Mapped[str] = mapped_column(Text, default="ACTIVE", nullable=False)

    # DB has both start_at/end_at AND valid_from/valid_until (added by prior migration)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Extra columns added by prior hack
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    currency: Mapped[str | None] = mapped_column(Text, nullable=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # updated_at from DB
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    policyholder: Mapped["Policyholder"] = relationship("Policyholder", back_populates="policies")
    region: Mapped["MicroRegion"] = relationship("MicroRegion", back_populates="policies")
    # trigger_rule via trigger_rule_id FK on this table
    trigger_rule: Mapped["TriggerRule"] = relationship(
        "TriggerRule", back_populates="policies",
        foreign_keys=[trigger_rule_id], uselist=False
    )
    # Also allow reverse lookup from TriggerRule.policy_id
    trigger_rule_reverse: Mapped["TriggerRule"] = relationship(
        "TriggerRule", back_populates="policy_reverse",
        foreign_keys="TriggerRule.policy_id", uselist=False,
        viewonly=True
    )
    payouts: Mapped[list["Payout"]] = relationship("Payout", back_populates="policy")
    wallets: Mapped[list["Wallet"]] = relationship("Wallet", back_populates="policy")

    def is_currently_valid(self) -> bool:
        from datetime import timezone
        now = datetime.now(timezone.utc)

        # Use start_at/end_at if available, fall back to valid_from/valid_until
        vf = self.start_at or self.valid_from
        vu = self.end_at or self.valid_until

        if vf is None or vu is None:
            return self.status == "ACTIVE"

        # Ensure offset-aware
        if vf.tzinfo is None:
            vf = vf.replace(tzinfo=timezone.utc)
        if vu.tzinfo is None:
            vu = vu.replace(tzinfo=timezone.utc)

        return self.status == "ACTIVE" and vf <= now <= vu

    def __repr__(self) -> str:
        return f"<Policy id={self.id!r} status={self.status}>"


class TriggerRule(Base, TimestampMixin):
    """
    Defines the parametric trigger condition for a policy.
    For PS-F03: rainfall >= 100.0 mm within 60 minutes.
    
    DB columns: id, metric, threshold_operator, threshold_value, unit,
                observation_window_minutes, consensus_quorum, created_at,
                policy_id, consensus_tolerance
    """
    __tablename__ = "trigger_rules"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric: Mapped[str] = mapped_column(Text, nullable=False)
    threshold_operator: Mapped[str] = mapped_column(Text, nullable=False)
    threshold_value: Mapped[float] = mapped_column(Numeric, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    observation_window_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    consensus_quorum: Mapped[int] = mapped_column(Integer, default=2, nullable=True)

    # policy_id added via ALTER TABLE
    policy_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=True
    )
    consensus_tolerance: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    policies: Mapped["Policy"] = relationship(
        "Policy", back_populates="trigger_rule",
        foreign_keys="Policy.trigger_rule_id", uselist=False,
        viewonly=True
    )
    policy_reverse: Mapped["Policy"] = relationship(
        "Policy", back_populates="trigger_rule_reverse",
        foreign_keys=[policy_id], uselist=False,
        viewonly=True
    )

    def __repr__(self) -> str:
        return (
            f"<TriggerRule id={self.id!r} "
            f"metric={self.metric!r} {self.threshold_operator}{self.threshold_value}>"
        )
