"""
routers/notifications.py — Authenticated notification endpoints.

GET  /notifications                         → list user's notifications
POST /notifications/{notification_id}/acknowledge → acknowledge a notification

Ownership: JWT → Policyholder → only that user's notifications.
"""
import uuid as _uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.notification import Notification, NotificationStatus
from models.policyholder import Policyholder
from schemas.notification import (
    AcknowledgeResponse,
    NotificationListResponse,
    NotificationResponse,
)
from services.auth import get_current_policyholder

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> NotificationListResponse:
    """
    List the authenticated user's notifications, newest first.
    Only returns notifications owned by the current policyholder.
    """
    stmt = (
        select(Notification)
        .where(Notification.policyholder_id == policyholder.id)
        .order_by(Notification.created_at.desc())
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    total = await db.scalar(
        select(func.count(Notification.id)).where(Notification.policyholder_id == policyholder.id)
    )

    return NotificationListResponse(
        notifications=[
            NotificationResponse(
                notification_id=str(n.id),
                policyholder_id=str(n.policyholder_id),
                policy_id=str(n.policy_id),
                payout_id=str(n.payout_id),
                event_type=n.event_type,
                title=n.title,
                message=n.message,
                status=n.status,
                created_at=n.created_at,
                acknowledged_at=n.acknowledged_at,
                escalation_due_at=n.escalation_due_at,
                escalated_at=n.escalated_at,
                metadata=n.metadata_,
            )
            for n in notifications
        ],
        total=total or 0,
    )


@router.post("/{notification_id}/acknowledge", response_model=AcknowledgeResponse)
async def acknowledge_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    policyholder: Policyholder = Depends(get_current_policyholder),
) -> AcknowledgeResponse:
    """
    Acknowledge a notification. Idempotent — repeated calls are safe.

    Authorization: only the owning policyholder can acknowledge.
    Server generates the authoritative acknowledged_at timestamp.
    """
    try:
        notif_uuid = _uuid.UUID(notification_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_ID", "message": "Invalid notification ID format."},
        )

    notification = await db.scalar(
        select(Notification).where(Notification.id == notif_uuid)
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Notification not found."},
        )

    # Ownership check: notification must belong to the authenticated policyholder
    if notification.policyholder_id != policyholder.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "FORBIDDEN", "message": "You do not have permission to acknowledge this notification."},
        )

    # Idempotent / Escalated state check
    # If already acknowledged or escalated, we just record the timestamp if it's missing, but we do NOT revert an ESCALATED status back to ACKNOWLEDGED.
    if notification.status in (NotificationStatus.ACKNOWLEDGED.value, NotificationStatus.ESCALATED.value):
        if notification.acknowledged_at is None:
            notification.acknowledged_at = datetime.now(timezone.utc)
            await db.flush()
            await db.commit()
        return AcknowledgeResponse(
            notification_id=str(notification.id),
            status=notification.status,
            acknowledged_at=notification.acknowledged_at,
        )

    # First acknowledgement: server-authoritative timestamp
    now = datetime.now(timezone.utc)
    notification.status = NotificationStatus.ACKNOWLEDGED.value
    notification.acknowledged_at = now
    await db.flush()
    await db.commit()

    return AcknowledgeResponse(
        notification_id=str(notification.id),
        status=notification.status,
        acknowledged_at=notification.acknowledged_at,
    )
