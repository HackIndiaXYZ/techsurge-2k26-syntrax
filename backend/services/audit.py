"""
services/audit.py — Audit event writing utility.

Provides write_audit_event() used by all services.
Records are append-only. Never update or delete audit rows.

NOTE: The DB audit_events table does NOT have a policy_id column.
      entity_id and correlation_id are UUID columns.
"""
import uuid as uuid_mod
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from models.audit import AuditEvent, AuditEventType
from services.ids import new_uuid


def _to_uuid_or_none(val) -> uuid_mod.UUID | None:
    """Convert a string or UUID to uuid.UUID, or return None."""
    if val is None:
        return None
    if isinstance(val, uuid_mod.UUID):
        return val
    try:
        return uuid_mod.UUID(str(val))
    except (ValueError, AttributeError):
        return None


def _sanitize_metadata(data: dict | None) -> dict | None:
    """Convert UUIDs, Decimals, and other non-JSON types to serializable values."""
    if data is None:
        return None
    from decimal import Decimal
    result = {}
    for k, v in data.items():
        if isinstance(v, uuid_mod.UUID):
            result[k] = str(v)
        elif isinstance(v, Decimal):
            result[k] = float(v)
        elif isinstance(v, dict):
            result[k] = _sanitize_metadata(v)
        elif isinstance(v, (list, tuple)):
            result[k] = [str(x) if isinstance(x, uuid_mod.UUID) else float(x) if isinstance(x, Decimal) else x for x in v]
        else:
            result[k] = v
    return result


async def write_audit_event(
    db: AsyncSession,
    event_type: AuditEventType,
    entity_type: str,
    entity_id: str,
    status: str,
    policy_id=None,  # accepted but NOT stored (no column in DB)
    correlation_id=None,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> AuditEvent:
    """
    Append an audit event to the audit_events table.
    Always use db.flush() (not commit) — the calling service owns the transaction.
    """
    now = datetime.now(timezone.utc)
    event = AuditEvent(
        id=new_uuid(),
        event_type=event_type.value if isinstance(event_type, AuditEventType) else str(event_type),
        entity_type=entity_type,
        entity_id=_to_uuid_or_none(entity_id),
        correlation_id=_to_uuid_or_none(correlation_id),
        actor="SYSTEM",
        status=status,
        message=message,
        metadata_=_sanitize_metadata(metadata),
        occurred_at=now,
        updated_at=now,
        created_at=now,
    )
    db.add(event)
    await db.flush()
    return event
