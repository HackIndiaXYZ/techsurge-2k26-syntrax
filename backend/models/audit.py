"""
models/audit.py — AuditEvent entity.

DB columns: id, correlation_id, entity_type, entity_id, event_type,
            actor, metadata, occurred_at, created_at, updated_at,
            status, message
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class AuditEventType(str, enum.Enum):
    TELEMETRY_RECEIVED = "TELEMETRY_RECEIVED"
    TELEMETRY_REJECTED = "TELEMETRY_REJECTED"
    TELEMETRY_DUPLICATE = "TELEMETRY_DUPLICATE"
    CONSENSUS_EVALUATED = "CONSENSUS_EVALUATED"
    CONSENSUS_REACHED = "CONSENSUS_REACHED"
    CONSENSUS_FAILED = "CONSENSUS_FAILED"
    TRIGGER_EVALUATED = "TRIGGER_EVALUATED"
    TRIGGER_FIRED = "TRIGGER_FIRED"
    TRIGGER_BLOCKED = "TRIGGER_BLOCKED"
    PAYOUT_CREATED = "PAYOUT_CREATED"
    PAYOUT_COMPLETED = "PAYOUT_COMPLETED"
    PAYOUT_FAILED = "PAYOUT_FAILED"
    WALLET_CREDITED = "WALLET_CREDITED"
    DUPLICATE_SETTLEMENT = "DUPLICATE_SETTLEMENT"


class AuditEvent(Base, TimestampMixin):
    """
    Audit log entry. Append-only.
    NOTE: entity_id and correlation_id are UUID in DB, but we accept
    string UUIDs and convert. policy_id is NOT a column in the DB.
    """
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    correlation_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)

    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)

    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    actor: Mapped[str | None] = mapped_column(Text, nullable=True)

    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<AuditEvent id={self.id!r} type={self.event_type} "
            f"entity={self.entity_type}/{self.entity_id}>"
        )
