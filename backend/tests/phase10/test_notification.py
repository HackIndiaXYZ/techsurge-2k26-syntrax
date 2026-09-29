import pytest
import uuid
import datetime
from httpx import AsyncClient
from sqlalchemy import select

from models.notification import Notification, NotificationStatus
from services.escalation import process_next_overdue_notification
from models.payout import Payout, PayoutStatus
from models.trigger import TriggerEvaluation, TriggerStatus
from models.consensus import ConsensusResult, ConsensusStatus

async def setup_notification_chain(db, test_data, is_old=False):
    cr = ConsensusResult(
        id=uuid.uuid4(),
        region_id=test_data["region_a"].id,
        metric="rainfall",
        window_start=datetime.datetime.now(datetime.timezone.utc),
        window_end=datetime.datetime.now(datetime.timezone.utc),
        status=ConsensusStatus.REACHED.value,
        quorum=2,
        consensus_value_mm=110.0
    )
    db.add(cr)
    
    te = TriggerEvaluation(
        id=uuid.uuid4(),
        policy_id=test_data["policy_a"].id,
        consensus_result_id=cr.id,
        trigger_status=TriggerStatus.TRIGGERED.value,
        evaluated_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(te)
    
    payout = Payout(
        id=uuid.uuid4(),
        policy_id=test_data["policy_a"].id,
        trigger_evaluation_id=te.id,
        wallet_id=test_data["wallet_a"].id,
        status=PayoutStatus.SUCCESS.value,
        amount_paise=100000,
        updated_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(payout)
    await db.flush()
    
    time_shift = datetime.timedelta(hours=25) if is_old else datetime.timedelta(0)
    now = datetime.datetime.now(datetime.timezone.utc)
    
    notif = Notification(
        id=uuid.uuid4(),
        policyholder_id=test_data["ph_a"].id,
        policy_id=test_data["policy_a"].id,
        payout_id=payout.id,
        event_type="SETTLEMENT",
        title="Test",
        message="Test message",
        status=NotificationStatus.UNREAD.value,
        escalation_due_at=now + datetime.timedelta(hours=3) - time_shift,
        created_at=now - time_shift
    )
    db.add(notif)
    await db.flush()
    return notif

@pytest.fixture
async def unread_notification(db, test_data):
    return await setup_notification_chain(db, test_data, is_old=False)

@pytest.mark.asyncio
async def test_notification_acknowledge_success(async_client: AsyncClient, test_data: dict, unread_notification, db):
    res = await async_client.post(f"/notifications/{unread_notification.id}/acknowledge", headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res.status_code == 200
    
    await db.refresh(unread_notification)
    assert unread_notification.status == NotificationStatus.ACKNOWLEDGED.value

@pytest.mark.asyncio
async def test_notification_acknowledge_cross_user(async_client: AsyncClient, test_data: dict, unread_notification):
    res = await async_client.post(f"/notifications/{unread_notification.id}/acknowledge", headers={"Authorization": f"Bearer {test_data['token_b']}"})
    assert res.status_code == 403

@pytest.mark.asyncio
async def test_notification_acknowledge_already_acknowledged(async_client: AsyncClient, test_data: dict, unread_notification, db):
    unread_notification.status = NotificationStatus.ACKNOWLEDGED.value
    db.add(unread_notification)
    await db.flush()

    res = await async_client.post(f"/notifications/{unread_notification.id}/acknowledge", headers={"Authorization": f"Bearer {test_data['token_a']}"})
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_escalation_job(db, test_data):
    notif = await setup_notification_chain(db, test_data, is_old=True)
    
    await process_next_overdue_notification(db)
    
    n = await db.scalar(select(Notification).where(Notification.id == notif.id))
    assert n.status == NotificationStatus.ESCALATED.value
