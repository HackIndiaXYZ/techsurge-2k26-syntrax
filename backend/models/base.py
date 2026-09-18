"""
models/base.py — SQLAlchemy declarative base and shared mixins.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Shared declarative base for all PS-F03 models."""
    pass


class ULIDPrimaryKeyMixin:
    """
    Mixin that provides a string primary key using ULID format.
    ULIDs are lexicographically sortable and time-ordered.
    We store as VARCHAR(26) for broad DB compatibility.
    """
    id: Mapped[str] = mapped_column(String(26), primary_key=True)


class TimestampMixin:
    """Mixin that adds created_at to any model."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

