"""
models/voice_call.py — Phase 6 Voice Call Job Record

Represents a durable job state for an outbound voice call.
Ensures idempotency (1:1 with AIAssistanceHandoff) and tracks retry behavior.
"""
import uuid
import enum

from sqlalchemy import ForeignKey, Text, JSON, Integer, DateTime
import datetime
from sqlalchemy import Uuid as PgUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin

class VoiceCallStatus(str, enum.Enum):
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    REQUESTED = "REQUESTED"
    CALLING = "CALLING"
    RINGING = "RINGING"
    ANSWERED = "ANSWERED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NO_ANSWER = "NO_ANSWER"
    BUSY = "BUSY"
    CANCELED = "CANCELED"
    RETRY_PENDING = "RETRY_PENDING"
    FAILED_FINAL = "FAILED_FINAL"
    BLOCKED = "BLOCKED"

class VoiceCallJob(Base, TimestampMixin):
    """
    Durable state machine for an outbound voice call.
    Guarantees:
    - 1:1 mapping with AIAssistanceHandoff via unique constraint.
    - Idempotency and controlled retries.
    """
    __tablename__ = "voice_call_jobs"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 1:1 linked Handoff
    handoff_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("ai_assistance_handoffs.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    
    policyholder_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("policyholders.id", ondelete="CASCADE"), nullable=False
    )
    
    phone_number: Mapped[str] = mapped_column(Text, nullable=False)
    
    status: Mapped[str] = mapped_column(Text, nullable=False, default=VoiceCallStatus.PENDING.value)
    
    provider_call_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    call_script_metadata: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)

    requested_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    answered_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    handoff: Mapped["AIAssistanceHandoff"] = relationship("AIAssistanceHandoff")
    policyholder: Mapped["Policyholder"] = relationship("Policyholder")

    def __repr__(self) -> str:
        return f"<VoiceCallJob id={self.id!r} status={self.status} phone={self.phone_number}>"


class CallLog(Base, TimestampMixin):
    """
    Immutable event history for provider webhooks.
    """
    __tablename__ = "call_logs"

    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    voice_call_job_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("voice_call_jobs.id", ondelete="CASCADE"), nullable=False
    )
    provider_call_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    provider_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    payload_metadata: Mapped[dict | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)

    job: Mapped["VoiceCallJob"] = relationship("VoiceCallJob")

    def __repr__(self) -> str:
        return f"<CallLog id={self.id!r} event={self.event_type} job={self.voice_call_job_id!r}>"
