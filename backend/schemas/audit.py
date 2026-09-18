"""
schemas/audit.py — Audit event response schemas.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    audit_id: str
    event_type: str
    entity_type: str
    entity_id: str
    policy_id: str | None = None
    correlation_id: str | None = None
    status: str
    message: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime


class AuditListResponse(BaseModel):
    policy_id: str
    total: int
    events: list[AuditEventResponse]

