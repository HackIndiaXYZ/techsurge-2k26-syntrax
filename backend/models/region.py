"""
models/region.py — MicroRegion entity.

DB columns: id, code, name, timezone, active, created_at, updated_at
"""
import uuid

from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class MicroRegion(Base, TimestampMixin):
    """
    A geographic micro-region covered by climate insurance.
    """
    __tablename__ = "micro_regions"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    timezone: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    policies: Mapped[list["Policy"]] = relationship(
        "Policy", back_populates="region", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<MicroRegion id={self.id!r} name={self.name!r}>"
