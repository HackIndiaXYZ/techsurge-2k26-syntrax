"""
models/consensus.py — ConsensusResult entity.

Records the output of the consensus evaluation for a set of telemetry events.

DB columns: id, region_id, metric, window_start, window_end, status,
            consensus_value_mm, quorum, created_at, policy_id,
            median_all_sources_mm, source_count_total, source_count_accepted,
            source_count_outliers, accepted_source_ids, outlier_source_ids, reason
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Numeric, Text, JSON, Uuid as PgUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class ConsensusStatus(str, enum.Enum):
    REACHED = "REACHED"
    NO_CONSENSUS = "NO_CONSENSUS"


class ConsensusResult(Base, TimestampMixin):
    """
    The output of a consensus computation over a set of telemetry observations.
    """
    __tablename__ = "consensus_results"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False
    )
    metric: Mapped[str | None] = mapped_column(Text, nullable=True)
    window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    consensus_value_mm: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    quorum: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Columns added via ALTER TABLE
    policy_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), nullable=True
    )
    median_all_sources_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_count_total: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    source_count_accepted: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    source_count_outliers: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    accepted_source_ids: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    outlier_source_ids: Mapped[list | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    trigger_evaluation: Mapped["TriggerEvaluation"] = relationship(
        "TriggerEvaluation", back_populates="consensus_result", uselist=False
    )

    def __repr__(self) -> str:
        return f"<ConsensusResult id={self.id!r} status={self.status}>"
