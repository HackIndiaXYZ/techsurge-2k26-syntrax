"""
models/notification.py — Notification entity for post-settlement user communication.

Phase 4: Notifications are created only after a successful settlement.

Ownership chain:
    Policyholder → Notification
    Policy → Payout → Notification

DB columns: id, policyholder_id, policy_id, payout_id, event_type,
            title, message, status, created_at, acknowledged_at, metadata
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, JSON
from sqlalchemy import Uuid as PgUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class NotificationEventType(str, enum.Enum):
    SETTLEMENT = "SETTLEMENT"


class NotificationStatus(str, enum.Enum):
    UNREAD = "UNREAD"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    ESCALATED = "ESCALATED"


class Notification(Base, TimestampMixin):
    """
    A user notification record.

    Invariants:
    - Created ONLY after a successful settlement + wallet credit.
    - Idempotent: unique constraint on (payout_id, event_type) prevents duplicates.
    - Owned by a policyholder — resolved from JWT, never from client input.
    """
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership: who receives this notification
    policyholder_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policyholders.id", ondelete="CASCADE"), nullable=False
    )

    # Traceability: which policy and payout triggered this
    policy_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False
    )
    payout_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("payouts.id", ondelete="CASCADE"), nullable=False
    )

    # Notification content
    event_type: Mapped[str] = mapped_column(Text, nullable=False, default=NotificationEventType.SETTLEMENT.value)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default=NotificationStatus.UNREAD.value)

    # Timestamps
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escalation_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optional structured metadata (e.g., amount_paise, consensus_value)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON().with_variant(JSONB, "postgresql"), nullable=True)

    # Relationships
    policyholder: Mapped["Policyholder"] = relationship("Policyholder")
    policy: Mapped["Policy"] = relationship("Policy")
    payout: Mapped["Payout"] = relationship("Payout")

    def __repr__(self) -> str:
        return f"<Notification id={self.id!r} event={self.event_type} status={self.status}>"
