"""
services/escalation.py — Phase 5 Three-Hour Escalation Engine

This service handles the automated state transition of notifications
that remain unacknowledged past their escalation deadline.
It relies on the database for authoritative idempotency and atomic claiming.
"""
import logging
from datetime import datetime, timezone
import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.notification import Notification, NotificationStatus
from models.ai_assistance import AIAssistanceHandoff, AIAssistanceStatus
from services.ids import new_uuid

logger = logging.getLogger(__name__)


async def process_next_overdue_notification(db: AsyncSession) -> bool:
    """
    Finds one overdue notification, atomically claims it, and escalates it.
    
    This function uses SELECT ... FOR UPDATE SKIP LOCKED to ensure multiple
    workers can poll safely without deadlocks or duplicate escalations.
    
    Returns True if a notification was escalated, False if none were found.
    """
    now = datetime.now(timezone.utc)
    
    async with db.begin_nested():
        # Atomically find and lock one overdue notification
        stmt = (
            select(Notification)
            .where(
                Notification.status == NotificationStatus.UNREAD.value,
                Notification.acknowledged_at.is_(None),
                Notification.escalation_due_at <= now
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        
        result = await db.execute(stmt)
        notification = result.scalar_one_or_none()
        
        if not notification:
            return False
            
        logger.info(f"Escalating overdue notification {notification.id}")
        
        # Mark as escalated
        notification.status = NotificationStatus.ESCALATED.value
        notification.escalated_at = now
        
        # Create the AI Assistance Handoff record (the explicit Phase 6 bridge)
        handoff = AIAssistanceHandoff(
            id=new_uuid(),
            notification_id=notification.id,
            policyholder_id=notification.policyholder_id,
            policy_id=notification.policy_id,
            payout_id=notification.payout_id,
            status=AIAssistanceStatus.PENDING.value,
            context_metadata={
                "escalated_at": now.isoformat(),
                "event_type": notification.event_type
            }
        )
        db.add(handoff)
        
        # The transaction will commit these changes together
        
    logger.info(f"Successfully escalated notification {notification.id}, created AI handoff {handoff.id}")
    return True


async def process_all_overdue_notifications(db: AsyncSession) -> int:
    """
    Processes overdue notifications until no more are found.
    Returns the total number escalated.
    """
    count = 0
    while True:
        try:
            processed = await process_next_overdue_notification(db)
            if not processed:
                break
            count += 1
        except Exception as e:
            logger.error(f"Error processing escalations: {e}", exc_info=True)
            break
            
    return count
