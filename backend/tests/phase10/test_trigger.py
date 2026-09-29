import pytest
import datetime
import uuid
from services.trigger import evaluate_trigger, RAINFALL_THRESHOLD_MM
from models.trigger import TriggerEvaluation, TriggerStatus
from models.consensus import ConsensusResult, ConsensusStatus
from models.policy import Policy, TriggerRule

@pytest.fixture
def mock_policy():
    policy_id = uuid.uuid4()
    # Mocking TriggerRule since evaluate_trigger uses db.scalar, we might need a real DB or we test the pure logic?
    # Wait, evaluate_trigger is async and takes db session because it loads TriggerRule from db.
    # To test purely, we should test it against the db or refactor.
    # Let's test with real DB session to be safe.
    pass

@pytest.mark.asyncio
async def test_trigger_boundary_below(db, test_data):
    policy = test_data["policy_a"]
    cr = ConsensusResult(
        id=uuid.uuid4(), region_id=test_data["region_a"].id, metric="rainfall",
        window_start=datetime.datetime.now(datetime.timezone.utc),
        window_end=datetime.datetime.now(datetime.timezone.utc),
        status=ConsensusStatus.REACHED, quorum=2, consensus_value_mm=99.0
    )
    db.add(cr)
    await db.flush()

    eval_result = await evaluate_trigger(cr, policy, str(uuid.uuid4()), db)
    assert eval_result.trigger_status == TriggerStatus.NOT_TRIGGERED

@pytest.mark.asyncio
async def test_trigger_boundary_exact(db, test_data):
    policy = test_data["policy_a"]
    cr = ConsensusResult(
        id=uuid.uuid4(), region_id=test_data["region_a"].id, metric="rainfall",
        window_start=datetime.datetime.now(datetime.timezone.utc),
        window_end=datetime.datetime.now(datetime.timezone.utc),
        status=ConsensusStatus.REACHED, quorum=2, consensus_value_mm=100.0
    )
    db.add(cr)
    await db.flush()

    eval_result = await evaluate_trigger(cr, policy, str(uuid.uuid4()), db)
    assert eval_result.trigger_status == TriggerStatus.TRIGGERED

@pytest.mark.asyncio
async def test_trigger_boundary_above(db, test_data):
    policy = test_data["policy_a"]
    cr = ConsensusResult(
        id=uuid.uuid4(), region_id=test_data["region_a"].id, metric="rainfall",
        window_start=datetime.datetime.now(datetime.timezone.utc),
        window_end=datetime.datetime.now(datetime.timezone.utc),
        status=ConsensusStatus.REACHED, quorum=2, consensus_value_mm=110.0
    )
    db.add(cr)
    await db.flush()

    eval_result = await evaluate_trigger(cr, policy, str(uuid.uuid4()), db)
    assert eval_result.trigger_status == TriggerStatus.TRIGGERED
