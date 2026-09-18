"""
models/telemetry.py — TelemetryEvent entity.

Each TelemetryEvent is one rainfall observation from one weather source.
event_id uniqueness is enforced at the DB level for deduplication.
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class TelemetryEvent(Base, TimestampMixin):
    """
    A single telemetry observation from a weather source.

    DEDUPLICATION:
    - event_id must be unique across the table.
    - A replayed event_id is rejected (returns DUPLICATE, not inserted).

    IMPORTANT:
    - value_mm is stored as Float (physical measurement — not monetary).
    - Monetary values are NEVER stored as Float in this system.
    """
    __tablename__ = "telemetry_events"

    # Internal DB primary key (ULID)
    id: Mapped[str] = mapped_column(String(26), primary_key=True)

    # Client-provided event identity — UNIQUE constraint for deduplication
    event_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)

    source_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("weather_sources.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    region_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    # Measurement
    metric: Mapped[str] = mapped_column(String(64), nullable=False)   # "rainfall"
    value_mm: Mapped[float] = mapped_column(Float, nullable=False)     # physical, not monetary
    unit: Mapped[str] = mapped_column(String(16), nullable=False)      # "mm"

    # Timestamps
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Validation status
    is_valid: Mapped[bool] = mapped_column(default=True, nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Relationships
    source: Mapped["WeatherSource"] = relationship("WeatherSource", back_populates="telemetry_events")

    def __repr__(self) -> str:
        return (
            f"<TelemetryEvent event_id={self.event_id!r} "
            f"source={self.source_id!r} value={self.value_mm}mm>"
        )

