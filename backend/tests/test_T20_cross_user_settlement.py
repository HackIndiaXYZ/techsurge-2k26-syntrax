import pytest
import pytest_asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from models.policyholder import Policyholder
from models.policy import Policy, PolicyStatus, TriggerRule
from models.wallet import Wallet
from services.simulation import run_simulation
from schemas.simulation import SimulationRequest, ObservationInput
from seeds.seed_demo_data import REGION_ID, SOURCE_IDS

def make_obs(a: float, b: float, c: float) -> list[ObservationInput]:
    return [
        ObservationInput(source_id=str(SOURCE_IDS[0]), value=a),
        ObservationInput(source_id=str(SOURCE_IDS[1]), value=b),
        ObservationInput(source_id=str(SOURCE_IDS[2]), value=c),
    ]

@pytest.mark.asyncio
async def test_cross_user_settlement(db: AsyncSession):
    # Setup User A and Policy A and Wallet A
    ph_a = Policyholder(id=uuid.uuid4(), display_name="User A")
    db.add(ph_a)
    policy_a = Policy(
        id=uuid.uuid4(),
        policyholder_id=ph_a.id,
        region_id=REGION_ID,
        name="Policy A",
        currency="INR",
        payout_amount_paise=1000000,
        status=PolicyStatus.ACTIVE
    )
    db.add(policy_a)
    db.add(TriggerRule(id=uuid.uuid4(), policy_id=policy_a.id, metric="rainfall", threshold_operator=">=", threshold_value=100.0, unit="mm", observation_window_minutes=60))
    wallet_a = Wallet(policyholder_id=ph_a.id, currency="INR", balance_paise=0)
    db.add(wallet_a)

    # Setup User B and Policy B and Wallet B
    ph_b = Policyholder(id=uuid.uuid4(), display_name="User B")
    db.add(ph_b)
    policy_b = Policy(
        id=uuid.uuid4(),
        policyholder_id=ph_b.id,
        region_id=REGION_ID,
        name="Policy B",
        currency="INR",
        payout_amount_paise=1000000,
        status=PolicyStatus.ACTIVE
    )
    db.add(policy_b)
    db.add(TriggerRule(id=uuid.uuid4(), policy_id=policy_b.id, metric="rainfall", threshold_operator=">=", threshold_value=100.0, unit="mm", observation_window_minutes=60))
    wallet_b = Wallet(policyholder_id=ph_b.id, currency="INR", balance_paise=0)
    db.add(wallet_b)
    
    await db.commit()
    
    # Refresh to ensure we have IDs
    await db.refresh(ph_a)
    await db.refresh(policy_a)
    await db.refresh(wallet_a)
    
    await db.refresh(ph_b)
    await db.refresh(policy_b)
    await db.refresh(wallet_b)

    # Run settlement for Policy A
    request_a = SimulationRequest(
        scenario="NORMAL",
        policy_id=str(policy_a.id),
        region_id=str(REGION_ID),
        observations=make_obs(110.0, 108.0, 111.0),
        observed_at=datetime(2026, 9, 18, 11, 0, 0, tzinfo=timezone.utc),
    )
    r1 = await run_simulation(request=request_a, db=db)
    await db.commit()
    assert r1.settlement.status == "SUCCESS", f"Trigger: {r1.trigger}, Consensus: {r1.consensus}"
    
    # Verify Wallet A got 1000000 and Wallet B is 0
    await db.refresh(wallet_a)
    await db.refresh(wallet_b)
    assert wallet_a.balance_paise == 1000000
    assert wallet_b.balance_paise == 0

    # Run settlement for Policy B
    request_b = SimulationRequest(
        scenario="NORMAL",
        policy_id=str(policy_b.id),
        region_id=str(REGION_ID),
        observations=make_obs(110.0, 108.0, 111.0),
        observed_at=datetime(2026, 9, 18, 11, 10, 0, tzinfo=timezone.utc),
    )
    r2 = await run_simulation(request=request_b, db=db)
    await db.commit()
    assert r2.settlement.status == "SUCCESS"
    
    # Verify Wallet B got 1000000 and Wallet A is still 1000000 (unchanged)
    await db.refresh(wallet_a)
    await db.refresh(wallet_b)
    assert wallet_a.balance_paise == 1000000
    assert wallet_b.balance_paise == 1000000
