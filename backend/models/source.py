"""
models/source.py — WeatherSource entity.

DB columns: id, code, kind, enabled, created_at, updated_at
"""
import uuid

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class WeatherSource(Base, TimestampMixin):
    """
    A weather data source.
    DB uses: code (text), kind (text), enabled (bool).
    """
    __tablename__ = "weather_sources"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    telemetry_events: Mapped[list["TelemetryEvent"]] = relationship(
        "TelemetryEvent", back_populates="source", lazy="select"
    )

    # Compatibility properties
    @property
    def name(self) -> str:
        return self.code

    @property
    def is_active(self) -> bool:
        return self.enabled

    def __repr__(self) -> str:
        return f"<WeatherSource id={self.id!r} code={self.code!r}>"
