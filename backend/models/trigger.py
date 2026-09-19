"""
models/trigger.py — TriggerEvaluation entity.

Records every deterministic trigger evaluation, whether it fired or not.
This is the immutable evidence of why a payout was or was not authorized.

DB columns: id, policy_id, consensus_result_id, trigger_status, reason,
            evaluated_at, consensus_value_mm, threshold_mm
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class TriggerStatus(str, enum.Enum):
    TRIGGERED = "TRIGGERED"
    NOT_TRIGGERED = "NOT_TRIGGERED"
    TRIGGER_BLOCKED_NO_CONSENSUS = "TRIGGER_BLOCKED_NO_CONSENSUS"


class TriggerEvaluation(Base):
    """
    One deterministic trigger evaluation.
    No created_at/updated_at — uses evaluated_at instead.
    """
    __tablename__ = "trigger_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False
    )
    consensus_result_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("consensus_results.id", ondelete="RESTRICT"), nullable=False
    )

    trigger_status: Mapped[str] = mapped_column(Text, nullable=False)

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Physical measurement — Float is correct (not monetary)
    consensus_value_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_mm: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    consensus_result: Mapped["ConsensusResult"] = relationship(
        "ConsensusResult", back_populates="trigger_evaluation"
    )
    payout: Mapped["Payout"] = relationship(
        "Payout", back_populates="trigger_evaluation", uselist=False
    )

    def __repr__(self) -> str:
        return f"<TriggerEvaluation id={self.id!r} status={self.trigger_status}>"
