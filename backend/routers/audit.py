"""
routers/audit.py — GET /policies/{policy_id}/audit
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.audit import AuditEvent
from models.policy import Policy
from schemas.audit import AuditEventResponse, AuditListResponse

router = APIRouter(prefix="/policies", tags=["Audit"])


@router.get("/{policy_id}/audit", response_model=AuditListResponse)
async def get_policy_audit(
    policy_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> AuditListResponse:
    # Verify policy exists
    policy = await db.get(Policy, policy_id)
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": f"Policy {policy_id!r} not found."},
        )

    # Count total audit events for this policy
    total = await db.scalar(
        select(func.count()).where(AuditEvent.policy_id == policy_id)
    )

    # Fetch most recent events first
    events_q = await db.execute(
        select(AuditEvent)
        .where(AuditEvent.policy_id == policy_id)
        .order_by(AuditEvent.created_at.desc())
        .limit(limit)
    )
    events = events_q.scalars().all()

    return AuditListResponse(
        policy_id=policy_id,
        total=total or 0,
        events=[
            AuditEventResponse(
                audit_id=e.id,
                event_type=e.event_type.value,
                entity_type=e.entity_type,
                entity_id=e.entity_id,
                policy_id=e.policy_id,
                correlation_id=e.correlation_id,
                status=e.status,
                message=e.message,
                metadata=e.metadata_,
                created_at=e.created_at,
            )
            for e in events
        ],
    )

