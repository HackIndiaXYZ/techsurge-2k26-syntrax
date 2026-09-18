"""
models/audit.py — AuditEvent entity.

Append-only audit log. Every significant state transition in the PS-F03
pipeline is recorded here.

NOT cryptographically tamper-proof (no blockchain, no Merkle tree).
Application-level append-only convention.
"""
import enum

from sqlalchemy import Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, TimestampMixin


class AuditEventType(str, enum.Enum):
    # Telemetry
    TELEMETRY_RECEIVED = "TELEMETRY_RECEIVED"
    TELEMETRY_REJECTED = "TELEMETRY_REJECTED"
    TELEMETRY_DUPLICATE = "TELEMETRY_DUPLICATE"

    # Consensus
    CONSENSUS_EVALUATED = "CONSENSUS_EVALUATED"
    CONSENSUS_REACHED = "CONSENSUS_REACHED"
    CONSENSUS_FAILED = "CONSENSUS_FAILED"

    # Trigger
    TRIGGER_EVALUATED = "TRIGGER_EVALUATED"
    TRIGGER_FIRED = "TRIGGER_FIRED"
    TRIGGER_BLOCKED = "TRIGGER_BLOCKED"

    # Settlement
    PAYOUT_CREATED = "PAYOUT_CREATED"
    PAYOUT_COMPLETED = "PAYOUT_COMPLETED"
    PAYOUT_FAILED = "PAYOUT_FAILED"

    # Wallet
    WALLET_CREDITED = "WALLET_CREDITED"

    # Idempotency
    DUPLICATE_SETTLEMENT = "DUPLICATE_SETTLEMENT"


class AuditEvent(Base, TimestampMixin):
    """
    Audit log entry. Written at every important state transition.
    Records are intended to be append-only (never updated/deleted in normal operation).
    """
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)

    event_type: Mapped[AuditEventType] = mapped_column(
        Enum(AuditEventType), nullable=False, index=True
    )

    # What entity this event is about
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)   # "PAYOUT", "WALLET", etc.
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    # Policy context (nullable for global events)
    policy_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("policies.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Correlation ID links all events from one simulation/request
    correlation_id: Mapped[str | None] = mapped_column(String(26), nullable=True, index=True)

    status: Mapped[str] = mapped_column(String(64), nullable=False)   # "SUCCESS", "FAILED", etc.
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Arbitrary structured metadata (JSON)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<AuditEvent id={self.id!r} type={self.event_type} "
            f"entity={self.entity_type}/{self.entity_id}>"
        )

