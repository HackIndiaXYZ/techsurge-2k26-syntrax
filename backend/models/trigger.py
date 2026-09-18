"""
models/trigger.py — TriggerEvaluation entity.

Records every deterministic trigger evaluation, whether it fired or not.
This is the immutable evidence of why a payout was or was not authorized.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class TriggerStatus(str, enum.Enum):
    TRIGGERED = "TRIGGERED"
    NOT_TRIGGERED = "NOT_TRIGGERED"
    TRIGGER_BLOCKED_NO_CONSENSUS = "TRIGGER_BLOCKED_NO_CONSENSUS"


class TriggerEvaluation(Base, TimestampMixin):
    """
    One deterministic trigger evaluation.

    trigger_evaluation_id is used as the idempotency anchor for settlement.
    A payout UNIQUE constraint on (policy_id, trigger_evaluation_id) ensures
    at-most-one wallet credit per qualifying event.

    AI MUST NOT alter trigger_status.
    """
    __tablename__ = "trigger_evaluations"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    policy_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    consensus_result_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("consensus_results.id", ondelete="RESTRICT"), nullable=False, unique=True
    )

    trigger_status: Mapped[TriggerStatus] = mapped_column(
        Enum(TriggerStatus), nullable=False, index=True
    )

    # Physical measurement — Float is correct (not monetary)
    consensus_value_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_mm: Mapped[float] = mapped_column(Float, nullable=False)

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Relationships
    consensus_result: Mapped["ConsensusResult"] = relationship(
        "ConsensusResult", back_populates="trigger_evaluation"
    )
    payout: Mapped["Payout"] = relationship(
        "Payout", back_populates="trigger_evaluation", uselist=False
    )

    def __repr__(self) -> str:
        return f"<TriggerEvaluation id={self.id!r} status={self.trigger_status}>"

