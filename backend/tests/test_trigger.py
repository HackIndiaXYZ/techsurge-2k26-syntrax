import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from models.trigger import TriggerStatus
from models.consensus import ConsensusResult, ConsensusStatus
from models.policy import Policy, TriggerRule
from services.trigger import evaluate_trigger
from services.ids import new_uuid

@pytest.fixture
def mock_db():
    db = AsyncMock()
    # Mock db.scalar to return a default TriggerRule
    rule = TriggerRule(id=new_uuid(), policy_id=new_uuid(), metric="RAINFALL_MM", threshold_operator=">=", threshold_value=100.0)
    db.scalar.return_value = rule
    return db

def make_policy(is_valid=True):
    p = Policy(id=new_uuid(), payout_amount_paise=1000000)
    p.is_currently_valid = MagicMock(return_value=is_valid)
    return p

def make_consensus(status: ConsensusStatus, value: float = None):
    return ConsensusResult(
        id=new_uuid(),
        policy_id=new_uuid(),
        region_id=new_uuid(),
        metric="RAINFALL_MM",
        window_start=datetime.now(timezone.utc),
        window_end=datetime.now(timezone.utc),
        status=status.value,
        consensus_value_mm=value,
        median_all_sources_mm=value,
        source_count_total=3,
        source_count_accepted=3,
        source_count_outliers=0,
        accepted_source_ids=[],
        outlier_source_ids=[],
        reason="Test"
    )

@pytest.mark.asyncio
async def test_trigger_above_threshold(mock_db):
    policy = make_policy()
    consensus = make_consensus(ConsensusStatus.REACHED, 110.0)
    result = await evaluate_trigger(consensus, policy, "corr-1", mock_db)
    assert result.trigger_status == TriggerStatus.TRIGGERED.value
    
@pytest.mark.asyncio
async def test_trigger_exact_threshold(mock_db):
    policy = make_policy()
    consensus = make_consensus(ConsensusStatus.REACHED, 100.00)
    result = await evaluate_trigger(consensus, policy, "corr-1", mock_db)
    assert result.trigger_status == TriggerStatus.TRIGGERED.value
    
@pytest.mark.asyncio
async def test_trigger_just_below_threshold(mock_db):
    policy = make_policy()
    consensus = make_consensus(ConsensusStatus.REACHED, 99.99)
    result = await evaluate_trigger(consensus, policy, "corr-1", mock_db)
    assert result.trigger_status == TriggerStatus.NOT_TRIGGERED.value

@pytest.mark.asyncio
async def test_trigger_zero(mock_db):
    policy = make_policy()
    consensus = make_consensus(ConsensusStatus.REACHED, 0.0)
    result = await evaluate_trigger(consensus, policy, "corr-1", mock_db)
    assert result.trigger_status == TriggerStatus.NOT_TRIGGERED.value

@pytest.mark.asyncio
async def test_trigger_no_consensus(mock_db):
    policy = make_policy()
    consensus = make_consensus(ConsensusStatus.NO_CONSENSUS, 120.0)
    result = await evaluate_trigger(consensus, policy, "corr-1", mock_db)
    assert result.trigger_status == TriggerStatus.TRIGGER_BLOCKED_NO_CONSENSUS.value

@pytest.mark.asyncio
async def test_trigger_disabled_policy(mock_db):
    policy = make_policy(is_valid=False)
    consensus = make_consensus(ConsensusStatus.REACHED, 110.0)
    result = await evaluate_trigger(consensus, policy, "corr-1", mock_db)
    assert result.trigger_status == TriggerStatus.NOT_TRIGGERED.value

@pytest.mark.asyncio
async def test_trigger_missing_policy_rule():
    db = AsyncMock()
    # Missing trigger rule!
    db.scalar.return_value = None
    
    policy = make_policy()
    consensus = make_consensus(ConsensusStatus.REACHED, 110.0)
    result = await evaluate_trigger(consensus, policy, "corr-1", db)
    
    # Requirement: "Missing/invalid policy configuration MUST fail safely. No payout authority may be produced."
    # If the current implementation falls back to 100.0, this will return TRIGGERED, failing the requirement.
    assert result.trigger_status == TriggerStatus.NOT_TRIGGERED.value
