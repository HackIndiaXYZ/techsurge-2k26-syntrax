"""
models/telemetry.py — TelemetryEvent entity.

DB columns: id, source_id, region_id, source_event_id, metric, value, unit,
            observed_at, window_start, window_end, received_at,
            validation_state, metadata, created_at
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, JSON, Uuid as PgUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class TelemetryEvent(Base, TimestampMixin):
    """
    A single telemetry observation from a weather source.
    """
    __tablename__ = "telemetry_events"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    source_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("weather_sources.id", ondelete="RESTRICT"), nullable=False
    )
    region_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False
    )

    # DB uses source_event_id, not event_id
    source_event_id: Mapped[str | None] = mapped_column(Text, nullable=True)

    metric: Mapped[str] = mapped_column(Text, nullable=False)
    value: Mapped[float | None] = mapped_column(Numeric, nullable=True)  # DB uses numeric, not float
    unit: Mapped[str] = mapped_column(Text, nullable=False)

    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    validation_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON().with_variant(JSONB, "postgresql"), nullable=True)

    # Relationships
    source: Mapped["WeatherSource"] = relationship("WeatherSource", back_populates="telemetry_events")

    # Compatibility properties
    @property
    def event_id(self) -> str | None:
        return self.source_event_id

    @property
    def value_mm(self) -> float | None:
        return float(self.value) if self.value is not None else None

    @property
    def is_valid(self) -> bool:
        return self.validation_state in (None, "ACCEPTED", "accepted")

    def __repr__(self) -> str:
        return (
            f"<TelemetryEvent id={self.id!r} "
            f"source={self.source_id!r} value={self.value}>"
        )
