"""
models/consensus.py — ConsensusResult entity.

Records the output of the consensus evaluation for a set of telemetry events.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class ConsensusStatus(str, enum.Enum):
    REACHED = "REACHED"
    NO_CONSENSUS = "NO_CONSENSUS"


class ConsensusResult(Base, TimestampMixin):
    """
    The output of a consensus computation over a set of telemetry observations.

    consensus_value_mm is None when status == NO_CONSENSUS.
    outlier_source_ids is a JSON array of source_id strings.
    accepted_source_ids is a JSON array of source_id strings.
    """
    __tablename__ = "consensus_results"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    policy_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("policies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    region_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False
    )

    status: Mapped[ConsensusStatus] = mapped_column(Enum(ConsensusStatus), nullable=False)

    # Physical measurement values — Float is correct here (not monetary)
    median_all_sources_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    consensus_value_mm: Mapped[float | None] = mapped_column(Float, nullable=True)

    source_count_total: Mapped[int] = mapped_column(Integer, nullable=False)
    source_count_accepted: Mapped[int] = mapped_column(Integer, nullable=False)
    source_count_outliers: Mapped[int] = mapped_column(Integer, nullable=False)

    # JSON arrays of source IDs
    accepted_source_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    outlier_source_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Relationships
    trigger_evaluation: Mapped["TriggerEvaluation"] = relationship(
        "TriggerEvaluation", back_populates="consensus_result", uselist=False
    )

    def __repr__(self) -> str:
        return f"<ConsensusResult id={self.id!r} status={self.status}>"

