"""
models/source.py — WeatherSource entity.

A WeatherSource represents one simulated weather telemetry provider.
For PS-F03 demo: source-a, source-b, source-c.
"""
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class WeatherSource(Base, TimestampMixin):
    """
    A simulated weather data source.
    Demo seeds: source-a, source-b, source-c.
    """
    __tablename__ = "weather_sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    region_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("micro_regions.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    region: Mapped["MicroRegion"] = relationship(
        "MicroRegion", back_populates="sources"
    )
    telemetry_events: Mapped[list["TelemetryEvent"]] = relationship(
        "TelemetryEvent", back_populates="source", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<WeatherSource id={self.id!r} region={self.region_id!r}>"

