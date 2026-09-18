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
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, Float, ForeignKey, Integer, String
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
    """
    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    region_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[PolicyStatus] = mapped_column(
        Enum(PolicyStatus), default=PolicyStatus.ACTIVE, nullable=False
    )

    # Payout — stored as integer paise (NEVER float)
    payout_amount_paise: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    region: Mapped["MicroRegion"] = relationship("MicroRegion", back_populates="policies")
    trigger_rule: Mapped["TriggerRule"] = relationship(
        "TriggerRule", back_populates="policy", uselist=False
    )
    payouts: Mapped[list["Payout"]] = relationship("Payout", back_populates="policy")
    wallets: Mapped[list["Wallet"]] = relationship("Wallet", back_populates="policy")

    def is_currently_valid(self) -> bool:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        
        # SQLite returns naive datetimes even for DateTime(timezone=True)
        # Ensure we are comparing offset-aware UTC datetimes
        valid_from = self.valid_from
        if valid_from.tzinfo is None:
            valid_from = valid_from.replace(tzinfo=timezone.utc)
            
        valid_until = self.valid_until
        if valid_until.tzinfo is None:
            valid_until = valid_until.replace(tzinfo=timezone.utc)
            
        return (
            self.status == PolicyStatus.ACTIVE
            and valid_from <= now <= valid_until
        )

    def __repr__(self) -> str:
        return f"<Policy id={self.id!r} status={self.status}>"


class TriggerRule(Base, TimestampMixin):
    """
    Defines the parametric trigger condition for a policy.
    For PS-F03: rainfall >= 100.0 mm within 60 minutes.
    """
    __tablename__ = "trigger_rules"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    policy_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    metric: Mapped[str] = mapped_column(String(64), nullable=False)          # "rainfall"
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)    # 100.0
    threshold_operator: Mapped[str] = mapped_column(String(4), nullable=False)  # ">="
    unit: Mapped[str] = mapped_column(String(16), nullable=False)            # "mm"
    observation_window_minutes: Mapped[int] = mapped_column(Integer, nullable=False)  # 60
    consensus_quorum: Mapped[int] = mapped_column(Integer, nullable=False)   # 2
    consensus_tolerance: Mapped[float] = mapped_column(Float, nullable=False) # 5.0

    # Relationship
    policy: Mapped["Policy"] = relationship("Policy", back_populates="trigger_rule")

    def __repr__(self) -> str:
        return (
            f"<TriggerRule policy={self.policy_id!r} "
            f"metric={self.metric!r} {self.threshold_operator}{self.threshold_value}>"
        )

