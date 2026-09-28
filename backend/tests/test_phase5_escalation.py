"""
tests/test_phase5_escalation.py — Phase 5 Escalation Engine Tests.
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from models.notification import Notification, NotificationStatus
from models.ai_assistance import AIAssistanceHandoff, AIAssistanceStatus
from services.notification import create_settlement_notification
from services.escalation import process_next_overdue_notification, process_all_overdue_notifications
from config import get_settings


from models.policy import Policy
import pytest_asyncio
import uuid

@pytest.fixture
def mock_settings(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "escalation_mode", "demo")
    monkeypatch.setattr(settings, "demo_escalation_window_seconds", 0)  # Instant escalation for tests
    return settings


@pytest_asyncio.fixture
async def user_policy(db):
    policy = await db.scalar(select(Policy).limit(1))
    return policy.policyholder_id, policy, uuid.uuid4()


@pytest.mark.asyncio
async def test_acknowledged_before_deadline(db, user_policy, mock_settings):
    """TEST 1 — ACKNOWLEDGED BEFORE DEADLINE"""
    policyholder_id, policy, payout_id = user_policy
    
    # Increase window to prevent instant escalation
    mock_settings.demo_escalation_window_seconds = 3600
    
    notification = await create_settlement_notification(
        policyholder_id, policy.id, payout_id, 1000000, db
    )
    
    assert notification.status == NotificationStatus.UNREAD.value
    
    # User acknowledges
    notification.status = NotificationStatus.ACKNOWLEDGED.value
    notification.acknowledged_at = datetime.now(timezone.utc)
    await db.commit()
    
    # Advance time artificially to pass the deadline
    # We'll just manually set the escalation_due_at to the past
    notification.escalation_due_at = datetime.now(timezone.utc) - timedelta(hours=1)
    await db.commit()
    
    # Run scheduler
    processed = await process_next_overdue_notification(db)
    assert not processed
    
    # Check DB
    await db.refresh(notification)
    assert notification.status == NotificationStatus.ACKNOWLEDGED.value
    assert notification.escalated_at is None
    
    handoffs = await db.scalars(select(AIAssistanceHandoff).where(AIAssistanceHandoff.notification_id == notification.id))
    assert len(handoffs.all()) == 0


@pytest.mark.asyncio
async def test_not_acknowledged_deadline_passed(db, user_policy, mock_settings):
    """TEST 2 — NOT ACKNOWLEDGED"""
    policyholder_id, policy, payout_id = user_policy
    
    # 0 second window -> instant escalation
    notification = await create_settlement_notification(
        policyholder_id, policy.id, payout_id, 1000000, db
    )
    
    # Run scheduler
    processed = await process_next_overdue_notification(db)
    assert processed
    
    await db.refresh(notification)
    assert notification.status == NotificationStatus.ESCALATED.value
    assert notification.escalated_at is not None
    
    handoffs = await db.scalars(select(AIAssistanceHandoff).where(AIAssistanceHandoff.notification_id == notification.id))
    handoffs_list = handoffs.all()
    assert len(handoffs_list) == 1
    assert handoffs_list[0].status == AIAssistanceStatus.PENDING.value


@pytest.mark.asyncio
async def test_duplicate_scheduler_execution(db, user_policy, mock_settings):
    """TEST 3 & 4 — DUPLICATE SCHEDULER EXECUTION & DUPLICATE AI HANDOFF"""
    policyholder_id, policy, payout_id = user_policy
    
    notification = await create_settlement_notification(
        policyholder_id, policy.id, payout_id, 1000000, db
    )
    
    # Run scheduler twice
    processed1 = await process_next_overdue_notification(db)
    processed2 = await process_next_overdue_notification(db)
    
    assert processed1 is True
    assert processed2 is False  # Second run should find nothing
    
    handoffs = await db.scalars(select(AIAssistanceHandoff).where(AIAssistanceHandoff.notification_id == notification.id))
    assert len(handoffs.all()) == 1


@pytest.mark.asyncio
async def test_acknowledgement_race_with_escalation(db, user_policy, mock_settings):
    """TEST 8 — ACKNOWLEDGEMENT RACE"""
    policyholder_id, policy, payout_id = user_policy
    
    notification = await create_settlement_notification(
        policyholder_id, policy.id, payout_id, 1000000, db
    )
    
    # Escalation runs and claims it
    await process_next_overdue_notification(db)
    await db.refresh(notification)
    
    # Simulate user trying to acknowledge it after it was escalated
    # Our API logic allows recording the timestamp but keeps status ESCALATED
    if notification.status in (NotificationStatus.ACKNOWLEDGED.value, NotificationStatus.ESCALATED.value):
        if notification.acknowledged_at is None:
            notification.acknowledged_at = datetime.now(timezone.utc)
            await db.commit()
            
    await db.refresh(notification)
    assert notification.status == NotificationStatus.ESCALATED.value
    assert notification.acknowledged_at is not None


@pytest.mark.asyncio
async def test_production_vs_demo_window(db, user_policy, monkeypatch):
    """TEST 6 & 7 — PRODUCTION & DEMO WINDOW CONFIGURATION"""
    policyholder_id, policy, payout_id = user_policy
    
    settings = get_settings()
    
    # Demo Mode
    monkeypatch.setattr(settings, "escalation_mode", "demo")
    monkeypatch.setattr(settings, "demo_escalation_window_seconds", 60)
    
    notif1 = await create_settlement_notification(policyholder_id, policy.id, payout_id, 1000000, db)
    delta1 = notif1.escalation_due_at - notif1.created_at
    assert 59 <= delta1.total_seconds() <= 61
    
    # Production Mode
    monkeypatch.setattr(settings, "escalation_mode", "production")
    
    import uuid
    notif2 = await create_settlement_notification(policyholder_id, policy.id, uuid.uuid4(), 1000000, db)
    delta2 = notif2.escalation_due_at - notif2.created_at
    assert 10799 <= delta2.total_seconds() <= 10801  # ~3 hours
