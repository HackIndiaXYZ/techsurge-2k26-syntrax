"""
models/ai_assistance.py — Phase 5 AI Assistance Handoff Record

Represents a durable handoff from the deterministic system to the AI assistance layer,
occurring after an escalation deadline passes without user acknowledgement.
"""
import uuid
import enum
from datetime import datetime

from sqlalchemy import ForeignKey, Text, JSON, DateTime
from sqlalchemy import Uuid as PgUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class AIAssistanceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class AIAssistanceHandoff(Base, TimestampMixin):
    """
    An explicit, idempotent handoff record for AI assistance.
    
    Guarantees:
    - 1:1 mapping with a notification via unique constraint.
    - AI does not make financial decisions; it relies on this deterministic trigger.
    """
    __tablename__ = "ai_assistance_handoffs"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 1:1 linked Notification
    notification_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    
    # Traceability
    policyholder_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policyholders.id", ondelete="CASCADE"), nullable=False
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False
    )
    payout_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("payouts.id", ondelete="CASCADE"), nullable=False
    )

    status: Mapped[str] = mapped_column(Text, nullable=False, default=AIAssistanceStatus.PENDING.value)
    
    # Any necessary context for the AI call
    context_metadata: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)

    # Relationships
    notification: Mapped["Notification"] = relationship("Notification")
    policyholder: Mapped["Policyholder"] = relationship("Policyholder")

    def __repr__(self) -> str:
        return f"<AIAssistanceHandoff id={self.id!r} notification_id={self.notification_id!r} status={self.status}>"
