"""
services/audit.py — Audit event writing utility.

Provides write_audit_event() used by all services.
Records are append-only. Never update or delete audit rows.
"""
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from models.audit import AuditEvent, AuditEventType
from services.ids import new_ulid


async def write_audit_event(
    db: AsyncSession,
    event_type: AuditEventType,
    entity_type: str,
    entity_id: str,
    status: str,
    policy_id: str | None = None,
    correlation_id: str | None = None,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """
    Append an audit event to the audit_events table.
    Always use db.flush() (not commit) — the calling service owns the transaction.
    """
    event = AuditEvent(
        id=new_ulid(),
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        policy_id=policy_id,
        correlation_id=correlation_id,
        status=status,
        message=message,
        metadata_=metadata,
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.flush()
    return event

