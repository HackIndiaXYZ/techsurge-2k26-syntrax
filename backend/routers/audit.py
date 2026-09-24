"""
routers/audit.py — GET /policies/{policy_id}/audit

NOTE: audit_events has no policy_id column. Events are linked to a policy
indirectly through entity_id. For the demo system (single policy), we return
all recent audit events ordered by created_at desc.
"""
import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.audit import AuditEvent
from models.policy import Policy
from schemas.audit import AuditEventResponse, AuditListResponse
from services.auth import get_current_user

router = APIRouter(prefix="/policies", tags=["Audit"])


@router.get("/{policy_id}/audit", response_model=AuditListResponse)
async def get_policy_audit(
    policy_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> AuditListResponse:
    try:
        pid = _uuid.UUID(policy_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_ID", "message": f"Invalid policy_id: {policy_id!r}"},
        )

    # Verify policy exists
    policy = await db.get(Policy, pid)
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Policy {policy_id!r} not found."},
        )

    # audit_events has no policy_id column — return all events for the demo system
    total = await db.scalar(select(func.count(AuditEvent.id)))

    events_q = await db.execute(
        select(AuditEvent)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
    )
    events = events_q.scalars().all()

    return AuditListResponse(
        policy_id=policy_id,
        total=total or 0,
        events=[
            AuditEventResponse(
                audit_id=str(e.id),
                event_type=e.event_type.value if hasattr(e.event_type, 'value') else str(e.event_type),
                entity_type=str(e.entity_type),
                entity_id=str(e.entity_id) if e.entity_id else "",
                policy_id=policy_id,  # synthesised for response
                correlation_id=str(e.correlation_id) if e.correlation_id else None,
                status=str(e.status) if e.status else "",
                message=e.message,
                metadata=e.metadata_,
                created_at=e.created_at,
            )
            for e in events
        ],
    )
