"""
services/notification.py — Notification creation service.

Called from the settlement engine ONLY after a successful payout + wallet credit.

Invariants:
- Notification is created in the SAME transaction as settlement.
- Idempotent: duplicate (payout_id, event_type) is caught and safely ignored.
- Notification is NEVER created for failed settlements.
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.notification import Notification, NotificationEventType, NotificationStatus
from services.ids import new_uuid

logger = logging.getLogger(__name__)


def _paise_to_inr_display(paise: int) -> str:
    """Convert paise to human-readable INR display. Integer-only."""
    rupees = paise // 100
    return f"\u20b9{rupees:,}"


async def create_settlement_notification(
    policyholder_id,
    policy_id,
    payout_id,
    amount_paise: int,
    db: AsyncSession,
) -> Notification | None:
    """
    Create a settlement notification for a successful payout.

    Idempotent: if a notification for this payout already exists, returns None.
    Must be called within the same DB transaction as the settlement.

    Args:
        policyholder_id: UUID of the policyholder (owner).
        policy_id: UUID of the policy that triggered settlement.
        payout_id: UUID of the payout record.
        amount_paise: Integer paise amount of the settlement.
        db: Active async DB session.

    Returns:
        The created Notification, or None if a duplicate already exists.
    """
    import uuid as _uuid

    # Idempotency: check if notification already exists for this payout
    existing = await db.scalar(
        select(Notification).where(
            Notification.payout_id == (payout_id if isinstance(payout_id, _uuid.UUID) else _uuid.UUID(str(payout_id))),
            Notification.event_type == NotificationEventType.SETTLEMENT.value,
        )
    )
    if existing is not None:
        logger.info(f"Settlement notification already exists for payout {payout_id}")
        return None

    amount_display = _paise_to_inr_display(amount_paise)

    notification = Notification(
        id=new_uuid(),
        policyholder_id=policyholder_id,
        policy_id=policy_id,
        payout_id=payout_id,
        event_type=NotificationEventType.SETTLEMENT.value,
        title="Settlement Triggered",
        message=(
            f"Your parametric insurance payout of {amount_display} has been triggered. "
            f"This is a deterministic settlement based on the weather index threshold. "
            f"The synthetic payout has been credited to your wallet."
        ),
        status=NotificationStatus.UNREAD.value,
        metadata_={
            "amount_paise": amount_paise,
            "amount_display": amount_display,
        },
    )

    try:
        async with db.begin_nested():
            db.add(notification)
            await db.flush()
    except IntegrityError:
        # Concurrent duplicate — safe to ignore
        logger.info(f"Duplicate settlement notification for payout {payout_id} (IntegrityError)")
        return None

    logger.info(f"Settlement notification created: {notification.id} for payout {payout_id}")
    return notification
