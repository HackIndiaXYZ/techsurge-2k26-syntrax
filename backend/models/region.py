"""
models/region.py — MicroRegion entity.

A MicroRegion represents a geographic area covered by a parametric policy.
For the PS-F03 demo: one region — "Kaveri Delta".
"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class MicroRegion(Base, TimestampMixin):
    """
    A geographic micro-region covered by climate insurance.
    Demo seed: region-kaveri-delta
    """
    __tablename__ = "micro_regions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    sources: Mapped[list["WeatherSource"]] = relationship(
        "WeatherSource", back_populates="region", lazy="select"
    )
    policies: Mapped[list["Policy"]] = relationship(
        "Policy", back_populates="region", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<MicroRegion id={self.id!r} name={self.name!r}>"

